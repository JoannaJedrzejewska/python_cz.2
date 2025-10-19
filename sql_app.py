import os
import random
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, ForeignKey, inspect, select, update, delete
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

engine = create_engine("sqlite:////tmp/sql_app.db", echo=True)
print(engine.connect())
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Experiment(Base):
    __tablename__ = 'experiments'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    type = Column(Integer)
    finished = Column(Boolean, default=False)
    #NOWY KOD - JEDNA DO WIELU
    data_points = relationship("DataPoint", back_populates="experiment", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"Experiment(id={self.id}, title='{self.title}', finished={self.finished})"

class DataPoint(Base):
    __tablename__ = 'data_points'
    id = Column(Integer, primary_key=True, index=True)
    real_value = Column(Float)
    target_value = Column(Float)
    
    #NOWY KOD
    experiment_id = Column(Integer, ForeignKey('experiments.id'), nullable=False)
    experiment = relationship("Experiment", back_populates="data_points")
    
    def __repr__(self):
        return f"DataPoint(id={self.id}, real_value={self.real_value}, target_value={self.target_value}, experiment_id={self.experiment_id})"
#NOWE _ USUWANIE BAZY
def drop_database():
    print("\n" + "="*50)
    print("USUWANIE BIEŻĄCEJ BAZY DANYCH")
    print("="*50)
    db_path = "./sql_app.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Usunięto plik bazy danych: {db_path}")
    else:
        print(f"Plik bazy danych nie istniał: {db_path}")
    print("-" * 50)

def show_table_definitions():
    print("\n" + "="*30)
    print("PODGLĄD ZDEFINIOWANYCH TABEL")
    print("="*30)
    if not Base.metadata.tables:
        print("Brak zdefiniowanych tabel w metadanych.")
        return
    for table_name, table_object in Base.metadata.tables.items():
        print(f"\n[TABLE] {table_name}")
        print("-" * (len(table_name) + 10))
        for column in table_object.columns:
            pk_info = " (PRIMARY KEY)" if column.primary_key else ""
            #NOWY KOD - FOREIGN KEY
            fk_info = " (FOREIGN KEY)" if column.foreign_keys else ""
            default_info = f" (DEFAULT: {column.default.arg})" if column.default else ""
            print(f"  {column.name}: {column.type}{pk_info}{fk_info}{default_info}")


def create_db_and_tables():
    print("\n--- Rozpoczęcie tworzenia tabel... ---")
    Base.metadata.create_all(bind=engine)
    print("--- Pomyślnie utworzono plik bazy danych oraz tabele. ---\n")

def run_data_operations():
    with SessionLocal() as session:
        print("="*50)
        print("WSTAWIANIE DANYCH")
        print("="*50)
        experiment_1 = Experiment(title="Test A/B", type=1)
        experiment_2 = Experiment(title="Optymalizacja Modelu", type=2)
        session.add_all([experiment_1, experiment_2])

        #NOWY KOD
        session.flush()
        
        data_points = []
        for i in range(1, 11):
            real = round(random.uniform(10.0, 50.0), 2)
            target = round(real * random.uniform(0.9, 1.1), 2)
            data_points.append(DataPoint(real_value=real, target_value=target, experiment_id=experiment_2.id))
        
        session.add_all(data_points)
        liczba_nowych_wierszy = len(session.new)
        session.commit()
        print(f"Dodano {liczba_nowych_wierszy} nowych wierszy")
        print("-" * 50)

        print("\n" + "="*30)
        print("POBIERANIE DANYCH")
        print("="*30)
        experiments = session.scalars(select(Experiment)).all()
        print("\n[Experiments]:")
        for exp in experiments:
            #NOWY KOD - WYŚWIETLANIE Z RELACJAMI
            print(f"  {exp}")
            print(f"    └─ Powiązane DataPoints: {len(exp.data_points)}")
            for dp in exp.data_points:
                print(f"       • {dp}")
        
        points = session.scalars(select(DataPoint)).all()
        print("\n[DataPoints - wszystkie]:")
        for point in points:
            print(f"  {point}")
        print("-" * 50)
        
        print("\n" + "="*30)
        print("AKTUALIZACJA DANYCH")
        print("="*30)
        stmt = update(Experiment).where(Experiment.finished == False).values(finished=True)
        result = session.execute(stmt)
        session.commit()
        print(f"Zaktualizowano {result.rowcount} wierszy w Experiments.")
        updated_experiments = session.scalars(select(Experiment)).all()
        print("\n[Experiments po aktualizacji]:")
        for exp in updated_experiments:
            print(f"  {exp}")
        print("-" * 50)

        #print("\n" + "="*30)
        #print("USUWANIE DANYCH")
        #print("="*30)
        #result_dp = session.execute(delete(DataPoint))
        #result_exp = session.execute(delete(Experiment))
        #session.commit()
        #print(f"Usunięto {result_exp.rowcount} wierszy z Experiments.")
        #print(f"Usunięto {result_dp.rowcount} wierszy z DataPoints.")
        #remaining_exp = session.scalars(select(Experiment)).all()
        #remaining_dp = session.scalars(select(DataPoint)).all()
        #print(f"\nPozostało w Experiments: {len(remaining_exp)}")
        #print(f"Pozostało w DataPoints: {len(remaining_dp)}")
        #print("-" * 50)

if __name__ == "__main__":
    #NOWE - usuwanie bazy
    drop_database() 
    show_table_definitions()
    create_db_and_tables()
    
    print("\n" + "="*30)
    print("Baza danych")
    print("="*30)
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        print(f"\n[TABLE] {table_name}")
        print("-" * (len(table_name) + 10))
        for column in inspector.get_columns(table_name):
            print(f"  {column['name']}: {column['type']} (PK: {column.get('primary_key')}, Default: {column.get('default')})")
        #NOWY KOD - WYŚWIETLANIE KLUCZY OBCYCH
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            print(f"\n  Klucze obce:")
            for fk in foreign_keys:
                print(f"    {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    run_data_operations()
