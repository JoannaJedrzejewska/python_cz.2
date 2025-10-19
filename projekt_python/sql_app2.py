import os
import random
from sqlalchemy import inspect, select, update, delete
from database import engine, SessionLocal, Base
from models import Experiment, DataPoint, Subject


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
            fk_info = " (FOREIGN KEY)" if column.foreign_keys else ""
            default_info = f" (DEFAULT: {column.default.arg})" if column.default else ""
            print(f"  {column.name}: {column.type}{pk_info}{fk_info}{default_info}")


def run_data_operations():
    with SessionLocal() as session:
        print("="*50)
        print("WSTAWIANIE DANYCH")
        print("="*50)
        
        experiment_1 = Experiment(title="Test A/B", type=1)
        experiment_2 = Experiment(title="Optymalizacja Modelu", type=2)
        session.add_all([experiment_1, experiment_2])
        session.flush()
        
        data_points = []
        for i in range(1, 11):
            real = round(random.uniform(10.0, 50.0), 2)
            target = round(real * random.uniform(0.9, 1.1), 2)
            data_points.append(DataPoint(real_value=real, target_value=target, experiment_id=experiment_2.id))
        
        session.add_all(data_points)
        
        subject_1 = Subject(gdpr_accepted=True)
        subject_2 = Subject(gdpr_accepted=False)
        subject_3 = Subject()
        
        session.add_all([subject_1, subject_2, subject_3])
        session.flush()
        
        experiment_1.subjects.append(subject_1)
        experiment_1.subjects.append(subject_2)
        experiment_2.subjects.append(subject_1)
        experiment_2.subjects.append(subject_3)
        
        session.commit()
        print(f"Dodano dane do bazy")
        print("-" * 50)

        print("\n" + "="*50)
        print("POBIERANIE DANYCH")
        print("="*50)
        experiments = session.scalars(select(Experiment)).all()
        print("\n[Experiments]:")
        for exp in experiments:
            print(f"  {exp}")
            print(f"    - Powiązane DataPoints: {len(exp.data_points)}")
            for dp in exp.data_points:
                print(f"       • {dp}")
            print(f"    - Powiązane Subjects: {len(exp.subjects)}")
            for subj in exp.subjects:
                print(f"       • {subj}")
        
        subjects = session.scalars(select(Subject)).all()
        print("\n[Subjects - wszystkie]:")
        for subj in subjects:
            print(f"  {subj}")
            print(f"    - Eksperymenty: {[exp.title for exp in subj.experiments]}")
        print("-" * 50)
        
        print("\n" + "="*50)
        print("AKTUALIZACJA DANYCH")
        print("="*50)
        stmt = update(Experiment).where(Experiment.finished == False).values(finished=True)
        result = session.execute(stmt)
        session.commit()
        print(f"Zaktualizowano {result.rowcount} wierszy")
        print("-" * 50)


if __name__ == "__main__":
    print("="*50)
    print("TWORZENIE TABEL")
    print("="*50)
    Base.metadata.create_all(bind=engine)
    print("Wszystkie tabele utworzone\n")
    
    show_table_definitions()
    
    print("\n" + "="*30)
    print("Inspekcja bazy danych")
    print("="*30)
    inspector = inspect(engine)
    for table_name in inspector.get_table_names():
        print(f"\n[TABLE] {table_name}")
        print("-" * (len(table_name) + 10))
        for column in inspector.get_columns(table_name):
            print(f"  {column['name']}: {column['type']} (PK: {column.get('primary_key')})")
        foreign_keys = inspector.get_foreign_keys(table_name)
        if foreign_keys:
            print(f"\n  Klucze obce:")
            for fk in foreign_keys:
                print(f"    {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    run_data_operations()
