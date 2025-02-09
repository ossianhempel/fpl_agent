from openai import OpenAI
import os
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv


class Prompt:
    """Manages all prompt templates and composition"""

    def __init__(self, prompt_dir: Optional[str] = None):
        self.prompt_dir = prompt_dir or Path("prompts")
        self._load_prompts()

    def _load_prompts(self):
        """Load prompt templates from files"""

        # TODO: format as XML and add examples
        # generate base SQL prompt
        self.sql_base = """
        You are a Postgres SQL expert assistant. Your task is to convert natural language questions 
        into SQL queries. Follow these rules:
        1. Only return the SQL query without any explanations
        2. Use proper SQL syntax and formatting
        3. Consider table relationships and join conditions
        4. Include appropriate WHERE clauses for filtering
        5. Use clear aliasing for joined tables
        """

        # prompt for handling errors
        self.sql_error = """
        The previous query resulted in an error. Please fix the following issues:
        {error_context}
        When generating the new query:
        1. Check table and column names
        2. Verify join conditions
        3. Validate syntax and semicolons
        4. Ensure proper quoting of string values
        """

        # prompt for schema context
        self.schema_context = """
        Available tables and their schemas:
        {schema}

        Key relationships:
        {relationships}
        """

    def build_initial_prompt(
        self, question: str, schema_info: Optional[dict] = None
    ) -> str:
        """Build the initial prompt for SQL generation"""
        prompt_parts = [self.sql_base]

        if schema_info:
            prompt_parts.append(
                self.schema_context.format(
                    schema=schema_info.get("tables", ""),
                    relationships=schema_info.get("relationships", ""),
                )
            )

        prompt_parts.append(f"Question: {question}")

        return "\n\n".join(prompt_parts)

    def build_error_prompt(
        self, question: str, error_context: str, schema_info: Optional[dict] = None
    ) -> str:
        """Build prompt to handle SQL errors"""
        prompt_parts = [
            self.sql_base,
            self.sql_error.format(error_context=error_context),
        ]

        if schema_info:
            prompt_parts.append(
                self.schema_context.format(
                    schema=schema_info.get("tables", ""),
                    relationships=schema_info.get("relationships", ""),
                )
            )

        prompt_parts.append(f"Question: {question}")
        return "\n\n".join(prompt_parts)


class LLMManager:
    """Manages LLM interactions and SQL generation"""

    def __init__(self, model_name: str = "gemini-2.0-flash-exp"):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )
        self.prompt = Prompt()
        self.schema_info: Optional[dict] = None
        self.model = model_name

    def set_schema_info(self, raw_schema: list):
        """Format raw schema (from databaseManager) for LLM prompts"""
        schema_string = []
        current_table = None

        for table_name, column_name, data_type in raw_schema:
            if table_name != current_table:
                if current_table is not None:
                    schema_string.append("")
                schema_string.append(f"Table: {table_name}")
                current_table = table_name
            schema_string.append(f" - {column_name}: {data_type}")

        tables_str = "\n".join(schema_string)

        relationships_str = """
        fact_player_performance.player_id -> dim_players.player_id
        fact_player_performance.team_id -> dim_teams.team_id
        fact_player_performance.gameweek_id -> dim_gameweeks.gameweek_id
        fact_player_performance.season_id -> dim_seasons.season_id
        fact_player_performance.date_id -> dim_dates.date_id
        fact_fixtures.home_team_id -> dim_teams.team_id
        fact_fixtures.away_team_id -> dim_teams.team_id
        """

        self.schema_info = {"tables": tables_str, "relationships": relationships_str}

    @staticmethod
    def _clean_sql_response(sql_response: str) -> str:
        """Clean up the SQL response from the LLM"""

        # remove code blocks if present
        clean_response = sql_response.replace("```sql", "").replace("```", "")

        # remove 'sql' prefix if present
        if clean_response.lower().startswith("sql"):
            clean_response = clean_response[3:]

        # clean up whitespace
        clean_response = clean_response.strip()

        # ensure query ends with semicolon
        if not clean_response.endswith(";"):
            clean_response += ";"

        return clean_response

    async def generate_sql(
        self, question: str, error_context: Optional[str] = None
    ) -> str:
        """Generate SQL query from user question"""
        try:
            if error_context:
                # build prompt with error construct
                prompt_text = self.prompt.build_error_prompt(
                    question=question,
                    error_context=error_context,
                    schema_info=self.schema_info,
                )
            else:
                # build initial prompt
                prompt_text = self.prompt.build_initial_prompt(
                    question=question, schema_info=self.schema_info
                )

            # generate sql response using the built prompt
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt_text},
                    {"role": "user", "content": question},
                ],
            )

            # Check if we have a valid response
            if not response.choices or not response.choices[0].message.content:
                raise Exception("No valid response received from LLM")

            # extract SQL from response
            sql_response = response.choices[0].message.content
            # clean and return SQL
            return self._clean_sql_response(sql_response)

        except Exception as e:
            raise Exception(f"SQL generation failed: {str(e)}")

    async def validate_sql(self, sql: str) -> bool:
        """Basic SQL validation"""
        # syntax validation logic
        required_elements = ["SELECT", "FROM"]
        sql_upper = sql.upper()
        return all(element in sql_upper for element in required_elements)


if __name__ == "__main__":
    import asyncio

    llm_manager = LLMManager()

    async def run_tests():
        question = "Show me the top 5 players with the most points"
        sql = await llm_manager.generate_sql(question)
        print(f"Generated SQL: \n{sql}")

        print("*" * 50)

        error_context = "Error: column 'points_scored' does not exist"
        sql_fixed = await llm_manager.generate_sql(question, error_context)
        print(f"Fixed SQL: \n{sql_fixed}")

    asyncio.run(run_tests())
