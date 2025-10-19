from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base

subject_experiment_association = Table(
    'subject_experiment',
    Base.metadata,
    Column('subject_id', Integer, ForeignKey('subjects.id'), primary_key=True),
    Column('experiment_id', Integer, ForeignKey('experiments.id'), primary_key=True)
)
class Experiment(Base):
    __tablename__ = 'experiments'
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    type = Column(Integer)
    finished = Column(Boolean, default=False)
    
    data_points = relationship("DataPoint", back_populates="experiment", cascade="all, delete-orphan")
    subjects = relationship("Subject", secondary=subject_experiment_association, back_populates="experiments")
    
    def __repr__(self):
        return f"Experiment(id={self.id}, title='{self.title}', finished={self.finished})"


class DataPoint(Base):
    __tablename__ = 'data_points' 
    id = Column(Integer, primary_key=True, index=True)
    real_value = Column(Float)
    target_value = Column(Float)
    experiment_id = Column(Integer, ForeignKey('experiments.id'), nullable=False)
    experiment = relationship("Experiment", back_populates="data_points")
    
    def __repr__(self):
        return f"DataPoint(id={self.id}, real_value={self.real_value}, target_value={self.target_value}, experiment_id={self.experiment_id})"

class Subject(Base):
    __tablename__ = 'subjects'
    id = Column(Integer, primary_key=True, index=True)
    gdpr_accepted = Column(Boolean, default=False)
    experiments = relationship("Experiment", secondary=subject_experiment_association, back_populates="subjects")
    
    def __repr__(self):
        return f"Subject(id={self.id}, gdpr_accepted={self.gdpr_accepted})"
