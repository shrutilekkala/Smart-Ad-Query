"""Generates a synthetic ad-campaign dataset and seeds the SQL database."""
import random
from datetime import date, timedelta

from .database import Base, SessionLocal, engine
from .models import Ad

PLATFORMS = ["Google Ads", "Meta Ads", "TikTok Ads", "LinkedIn Ads", "Amazon Ads"]

CAMPAIGNS = [
    ("Summer Sneaker Blowout", "Footwear", "18-34 sneakerheads"),
    ("Back-to-School Laptop Deals", "Electronics", "students & parents"),
    ("Organic Skincare Launch", "Beauty", "women 25-45 interested in clean beauty"),
    ("Plant-Based Meal Kits", "Food & Beverage", "health-conscious millennials"),
    ("B2B SaaS Free Trial Push", "Software", "startup founders & CTOs"),
    ("Holiday Toy Sale", "Retail", "parents with young children"),
    ("Fitness App Subscription Drive", "Health & Fitness", "gym-goers 20-40"),
    ("Luxury Watch Collection", "Fashion", "affluent professionals 30-55"),
    ("Budget Travel Packages", "Travel", "young adults seeking deals"),
    ("Home Office Furniture Sale", "Home & Garden", "remote workers"),
    ("Electric Vehicle Test Drive", "Automotive", "eco-conscious car buyers"),
    ("Pet Subscription Box", "Pets", "dog and cat owners"),
    ("Streaming Service Free Month", "Entertainment", "cord-cutters 18-40"),
    ("Craft Beer Delivery", "Food & Beverage", "beer enthusiasts 21-40"),
    ("Online Coding Bootcamp", "Education", "career changers"),
]

AD_COPY_TEMPLATES = [
    "Discover {campaign} — limited-time offer for {audience}. Shop now and save big.",
    "{campaign}: crafted for {audience} who want quality without compromise.",
    "Tired of the same old options? {campaign} brings something new for {audience}.",
    "Join thousands of {audience} who've already switched. {campaign} starts today.",
    "{campaign} — because {audience} deserve better. Limited stock available.",
    "Unlock exclusive savings on {campaign}, hand-picked for {audience}.",
    "The wait is over. {campaign} is here for {audience} everywhere.",
    "Rated #1 by {audience}. Experience {campaign} risk-free.",
]


def _random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


def generate_ads(n: int = 300, seed: int = 42) -> list[dict]:
    rng = random.Random(seed)
    start, end = date(2025, 1, 1), date(2025, 12, 31)
    ads = []
    for i in range(n):
        campaign_name, category, audience = rng.choice(CAMPAIGNS)
        platform = rng.choice(PLATFORMS)
        template = rng.choice(AD_COPY_TEMPLATES)
        ad_copy = template.format(campaign=campaign_name, audience=audience)

        impressions = rng.randint(2_000, 500_000)
        # base CTR varies by platform/category to create realistic, queryable variance
        base_ctr = rng.uniform(0.005, 0.08)
        clicks = max(1, int(impressions * base_ctr))
        cpc = rng.uniform(0.25, 4.5)
        spend = round(clicks * cpc, 2)
        conv_rate = rng.uniform(0.01, 0.12)
        conversions = max(0, int(clicks * conv_rate))
        avg_order_value = rng.uniform(15, 250)
        revenue = round(conversions * avg_order_value, 2)

        ads.append(
            dict(
                campaign_name=campaign_name,
                platform=platform,
                ad_copy=ad_copy,
                target_audience=audience,
                date=_random_date(start, end),
                impressions=impressions,
                clicks=clicks,
                spend=spend,
                conversions=conversions,
                revenue=revenue,
            )
        )
    return ads


def seed_database(n: int = 300, reset: bool = True) -> int:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if reset:
            db.query(Ad).delete()
            db.commit()
        elif db.query(Ad).count() > 0:
            return db.query(Ad).count()

        rows = generate_ads(n)
        db.bulk_insert_mappings(Ad, rows)
        db.commit()
        return len(rows)
    finally:
        db.close()


if __name__ == "__main__":
    count = seed_database()
    print(f"Seeded {count} ad records.")
