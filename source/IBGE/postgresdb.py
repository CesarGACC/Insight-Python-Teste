from sqlalchemy import create_engine



def create_database():
    engine = create_engine("postgresql://localhost/mydb")
    conn = engine.connect()
    conn.close()
