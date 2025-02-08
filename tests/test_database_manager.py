import pytest
from fpl_agent.db.database_manager import DatabaseManager
from dotenv import load_dotenv


@pytest.fixture
def db_manager():
    load_dotenv()
    manager = DatabaseManager()
    yield manager
    manager.close()


def test_DatabaseManager(db_manager):
    result = db_manager.execute_query(
        """
        select * from dbt_ohempel.dim_teams LIMIT 10
        """
    )

    assert result["data"] == [
        ("4fc9baf210346939946d5a49f255588b", "Arsenal"),
        ("568cd44a200f4fc62f6be6762ad799cf", "Aston Villa"),
        ("b436d55f36cfbe8a085c8b75fb7fe98a", "Bournemouth"),
        ("540133b526e452ace05d9e7d934e2fec", "Brentford"),
        ("0d84883ca72c88cb53c8a38262efdcbc", "Brighton"),
        ("cf13b16553629fc715acb8289d10374e", "Burnley"),
        ("8056df0882080a7c1d36f190f231f919", "Chelsea"),
        ("507469ae2d0be64d648ca88b63c4cabb", "Crystal Palace"),
        ("6414a61d98ab23b6d757e888ab17a66a", "Everton"),
        ("8cd5e94668b139c1f42a89a1e130f3cf", "Fulham"),
    ], "Query result didn't match expected result"
