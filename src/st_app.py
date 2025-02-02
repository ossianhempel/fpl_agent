from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
from fpl_agent import Agent

prompt=[
        """
        <prompt>
            <description>
                You are a SQL generator that creates accurate, efficient Postgres-compatible SQL queries based on user instructions. The schema below belongs to a database used for analyzing Fantasy Premier League data.
            </description>
            <schema>
                <table name="dbt_ohempel.dim_dates">
                <column name="date_id" type="TEXT" description="Unique identifier for dates." />
                <column name="date" type="TIMESTAMP" description="Actual date value." />
                <column name="year" type="NUMERIC" description="Year component." />
                <column name="month" type="NUMERIC" description="Month component." />
                <column name="day" type="NUMERIC" description="Day of the month." />
                <column name="day_of_week" type="NUMERIC" description="Numeric day of the week (e.g., 1 = Monday)." />
                <column name="day_of_year" type="NUMERIC" description="Day of the year." />
                <column name="quarter" type="NUMERIC" description="Quarter of the year." />
                <column name="week" type="NUMERIC" description="Week of the year." />
                <column name="day_name" type="TEXT" description="Full name of the day (e.g., Monday)." />
                <column name="month_name" type="TEXT" description="Full name of the month (e.g., January)." />
                <column name="is_weekend" type="BOOLEAN" description="True if the date is a weekend." />
                <column name="is_christmas" type="BOOLEAN" description="True if the date is Christmas." />
                <column name="is_new_year" type="BOOLEAN" description="True if the date is New Year." />
                </table>
                <table name="dbt_ohempel.dim_players">
                <column name="player_id" type="TEXT" description="Unique identifier for players." />
                <column name="player_name" type="TEXT" description="Name of the player." />
                <column name="player_cost" type="NUMERIC" description="Cost of the player." />
                <column name="position" type="TEXT" description="Position of the player (e.g., Defender)." />
                <column name="team_id" type="TEXT" description="ID of the team the player belongs to." />
                <column name="last_updated" type="TIMESTAMP" description="Timestamp of the last update." />
                </table>
                <table name="dbt_ohempel.fact_fixtures">
                <column name="fixture_id" type="INTEGER" description="Unique fixture identifier." />
                <column name="seasonal_fixture_id" type="INTEGER" description="Unique ID for the fixture within a season." />
                <column name="gameweek_id" type="TEXT" description="ID linking to the gameweek." />
                <column name="gameweek" type="INTEGER" description="Number of the gameweek." />
                <column name="season_id" type="TEXT" description="ID linking to the season." />
                <column name="season" type="TEXT" description="Name of the season." />
                <column name="date_id" type="TEXT" description="ID linking to the date." />
                <column name="date" type="TIMESTAMP" description="Date of the fixture." />
                <column name="home_team_id" type="TEXT" description="ID of the home team." />
                <column name="away_team_id" type="TEXT" description="ID of the away team." />
                <column name="kickoff_time" type="TIMESTAMP" description="Time the fixture starts." />
                <column name="finished" type="BOOLEAN" description="True if the fixture has finished." />
                <column name="finished_provisional" type="BOOLEAN" description="True if the fixture is provisionally marked as finished." />
                <column name="minutes" type="INTEGER" description="Minutes played." />
                <column name="provisional_start_time" type="BOOLEAN" description="True if the start time is provisional." />
                <column name="started" type="BOOLEAN" description="True if the fixture has started." />
                <column name="home_team_source_id" type="INTEGER" description="Source system ID of the home team." />
                <column name="away_team_source_id" type="INTEGER" description="Source system ID of the away team." />
                <column name="team_h_difficulty" type="INTEGER" description="Difficulty rating of the home team." />
                <column name="team_a_difficulty" type="INTEGER" description="Difficulty rating of the away team." />
                <column name="team_h_score" type="DOUBLE PRECISION" description="Score of the home team." />
                <column name="team_a_score" type="DOUBLE PRECISION" description="Score of the away team." />
                <column name="pulse_id" type="INTEGER" description="Unique ID for fixture pulse tracking." />
                </table>
                <table name="dbt_ohempel.dim_teams">
                <column name="team_id" type="TEXT" description="Unique identifier for teams." />
                <column name="team" type="TEXT" description="Name of the team." />
                </table>
                <table name="dbt_ohempel.fact_player_performance">
                <column name="player_performance_id" type="INTEGER" description="Unique identifier for player performance." />
                <column name="season" type="TEXT" description="Season name." />
                <column name="gameweek" type="INTEGER" description="Gameweek number." />
                <column name="date" type="TIMESTAMP" description="Date of the performance." />
                <column name="player_name" type="TEXT" description="Name of the player." />
                <column name="player_cost" type="NUMERIC" description="Cost of the player." />
                <column name="total_points" type="INTEGER" description="Total points scored by the player." />
                <column name="position" type="TEXT" description="Player position (e.g., Midfielder)." />
                <column name="team" type="TEXT" description="Team of the player." />
                <column name="opponent_team" type="TEXT" description="Opponent team." />
                <column name="team_a_score" type="INTEGER" description="Score of the away team." />
                <column name="team_h_score" type="INTEGER" description="Score of the home team." />
                <column name="was_home" type="BOOLEAN" description="True if the player played at home." />
                <column name="goals_scored" type="INTEGER" description="Goals scored by the player." />
                <column name="assists" type="INTEGER" description="Assists made by the player." />
                <column name="bonus" type="INTEGER" description="Bonus points earned." />
                <column name="bps" type="INTEGER" description="Bonus points system score." />
                <column name="clean_sheets" type="INTEGER" description="Clean sheets kept by the player." />
                <column name="creativity" type="NUMERIC" description="Creativity metric." />
                <column name="element" type="INTEGER" description="Player element ID." />
                <column name="xP" type="NUMERIC" description="Expected points." />
                <column name="expected_assists" type="NUMERIC" description="Expected assists." />
                <column name="expected_goal_involvements" type="NUMERIC" description="Expected goal involvements." />
                <column name="expected_goals" type="NUMERIC" description="Expected goals." />
                <column name="expected_goals_conceded" type="NUMERIC" description="Expected goals conceded." />
                <column name="goals_conceded" type="INTEGER" description="Goals conceded." />
                <column name="ict_index" type="NUMERIC" description="ICT index metric." />
                <column name="influence" type="NUMERIC" description="Influence metric." />
                <column name="kickoff_time" type="TIMESTAMP" description="Kickoff time." />
                <column name="minutes_played" type="INTEGER" description="Minutes played." />
                <column name="own_goals" type="INTEGER" description="Own goals scored." />
                <column name="penalties_missed" type="INTEGER" description="Penalties missed." />
                <column name="penalties_saved" type="INTEGER" description="Penalties saved." />
                <column name="red_cards" type="INTEGER" description="Red cards received." />
                <column name="saves" type="INTEGER" description="Saves made." />
                <column name="player_started" type="BOOLEAN" description="True if the player started the match." />
                <column name="threat" type="NUMERIC" description="Threat metric." />
                <column name="transfers_balance" type="INTEGER" description="Net transfers balance." />
                <column name="transfers_in" type="INTEGER" description="Transfers in." />
                <column name="transfers_out" type="INTEGER" description="Transfers out." />
                <column name="selected" type="INTEGER" description="Number of times the player was selected." />
                <column name="yellow_cards" type="INTEGER" description="Yellow cards received." />
                <column name="player_id" type="TEXT" description="Unique player identifier." />
                <column name="team_id" type="TEXT" description="Team ID." />
                <column name="fixture_id" type="INTEGER" description="Fixture ID." />
                <column name="gameweek_id" type="TEXT" description="Gameweek ID." />
                <column name="season_id" type="TEXT" description="Season ID." />
                <column name="date_id" type="TEXT" description="Date ID." />
                <column name="seasonal_fixture_id" type="INTEGER" description="Seasonal fixture ID." />
                </table>
                <table name="dbt_ohempel.dim_seasons">
                <column name="season_id" type="TEXT" description="Unique season identifier." />
                <column name="season" type="TEXT" description="Season name." />
                <column name="start_date" type="DATE" description="Start date of the season." />
                <column name="end_date" type="DATE" description="End date of the season." />
                </table>
                <table name="dbt_ohempel.dim_gameweeks">
                <column name="gameweek_id" type="TEXT" description="Unique identifier for the gameweek." />
                <column name="season" type="TEXT" description="Season name." />
                <column name="gameweek" type="INTEGER" description="Gameweek number." />
                <column name="start_date" type="DATE" description="Start date of the gameweek." />
                <column name="end_date" type="DATE" description="End date of the gameweek." />
                </table>
            </schema>
            <instructions>
                <point>Create a valid PostgreSQL SQL query based on user instructions.</point>
                <point>Do NOT use `QUALIFY` in any queries, as it is not supported in PostgreSQL.</point>
                <point>When filtering results based on window functions (e.g., `ROW_NUMBER` or `RANK`), use `WITH` clauses or subqueries.</point>
                <point>Ensure all table and column references match the schema.</point>
                <point>Include JOINs where necessary, properly matching keys (e.g., team_id, player_id, date_id).</point>
                <point>Apply WHERE conditions, filters, GROUP BY, or ORDER BY only if requested.</point>
                <point>Make the query readable with proper indentation and aliases if useful.</point>
            </instructions>
            <example>
                <request>Get the top-scoring player in each position for the 2023 season.</request>
                <sql><![CDATA[
                WITH ranked_players AS (
                    SELECT 
                        pp.player_name,
                        pp.position,
                        SUM(pp.total_points) AS total_points,
                        ROW_NUMBER() OVER (PARTITION BY pp.position ORDER BY SUM(pp.total_points) DESC) AS row_num
                    FROM 
                        dbt_ohempel.fact_player_performance AS pp
                    JOIN 
                        dbt_ohempel.dim_seasons AS s
                        ON pp.season_id = s.season_id
                    WHERE 
                        s.season = '2023-24'
                    GROUP BY 
                        pp.player_name, pp.position
                )
                SELECT 
                    player_name,
                    position,
                    total_points
                FROM 
                    ranked_players
                WHERE 
                    row_num = 1
                ORDER BY 
                    position, total_points DESC;
                ]]></sql>
            </example>

        """
    ]

st.set_page_config(page_title="I can Retrieve Any SQL query")
st.header("Gemini App To Retrieve SQL Data")

agent = Agent()

question = st.text_input("Input: ", key="input")

submit = st.button("Ask the question")

# if submit is clicked
if submit:
    response = agent.get_gemini_response(question=question, prompt=prompt)
    # TODO: if prompt starts or ends with ``` -> remove
    # TODO: if prompt starts with "sql" -> remove it
    print(response)
    clean_response = response.replace("```", "")
    if clean_response.startswith("sql"):
        clean_response = clean_response.replace("sql", "")
    data = agent.read_sql_query(clean_response)
    st.subheader("The response is:")
    for row in data:
        print(row)
        st.header(row)
