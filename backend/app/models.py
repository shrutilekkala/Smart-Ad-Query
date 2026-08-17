from sqlalchemy import Column, Date, Float, Integer, String, Text

from .database import Base


class Ad(Base):
    __tablename__ = "ads"

    id = Column(Integer, primary_key=True, index=True)
    campaign_name = Column(String, index=True, nullable=False)
    platform = Column(String, index=True, nullable=False)
    ad_copy = Column(Text, nullable=False)
    target_audience = Column(String, nullable=False)
    date = Column(Date, index=True, nullable=False)

    impressions = Column(Integer, nullable=False)
    clicks = Column(Integer, nullable=False)
    spend = Column(Float, nullable=False)
    conversions = Column(Integer, nullable=False)
    revenue = Column(Float, nullable=False)
