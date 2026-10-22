from src.report import generate_report

sources = """
[Source 1]
Title: Honey Basics
URL: https://example.com/honey
Text: Honey bees collect nectar from flowers and store it in their stomachs.
Back at the hive, they pass the nectar to other bees, which add enzymes that
break it into simple sugars. The bees then fan their wings to evaporate water
until the honey is about 17 percent water. A single bee makes only about
one twelfth of a teaspoon of honey in its whole life.

[Source 2]
Title: Hive Life
URL: https://example.com/hive
Text: A colony can hold 20,000 to 60,000 bees. Worker bees do most of the work,
while the queen lays up to 2,000 eggs per day. In winter the bees eat stored
honey to stay warm.
"""

report = generate_report(sources)

print("\nTITLE:", report.title)
print("SUMMARY:", report.summary)
for kp in report.key_points:
    print(f"- {kp.point}  (sources: {kp.source_ids})")