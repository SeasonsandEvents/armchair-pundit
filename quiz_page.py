"""Football general knowledge quiz page, built by build_pages.py.

Every question comes from a clue already published (and fact-checked) in one of
the season crosswords in index.html. Do not add a question here unless its fact
is in a published clue.
"""
import html

ROUNDS = [
    ("Round one: the 1990s", [
        ("Which broadcaster's television deal launched the Premier League in 1992?", "Sky"),
        ("Which manager retired in 1993 after 18 years at Nottingham Forest's City Ground?", "Brian Clough"),
        ("Alan Shearer joined Blackburn for a British record fee in 1992. Which club did he leave?", "Southampton"),
        ("Which club finished bottom in 1993–94, their first top-flight season, conceding 100 league goals?", "Swindon Town"),
        ("What was the nickname of Blackburn's title-winning strike partnership in 1994–95?", "The SAS"),
        ("In Manchester United's record 9–0 win over Ipswich in 1995, how many goals did one player score?", "Five"),
        ("Which Dutch forward joined Arsenal in the summer of 1995?", "Dennis Bergkamp"),
        ("Which 17-year-old scored on his debut at Selhurst Park in 1996–97?", "Michael Owen"),
        ("Which Manchester United youngster was voted PFA Young Player of the Year in 1997?", "David Beckham"),
        ("In 1997–98, Ian Wright became Arsenal's all-time top scorer against which club?", "Bolton Wanderers"),
    ]),
    ("Round two: the 2000s", [
        ("Which Dutch striker won the Golden Boot in 2000–01 with 23 goals?", "Jimmy Floyd Hasselbaink"),
        ("Chelsea's 2005 league title ended a wait of how many years?", "50"),
        ("Who was the first Chelsea player to win the PFA Players' Player of the Year award?", "John Terry"),
        ("How many league goals did Thierry Henry score to win the 2005–06 Golden Boot?", "27"),
        ("Which Watford goalkeeper was beaten by Paul Robinson's free-kick from his own half in 2006–07?", "Ben Foster"),
        ("Who scored Portsmouth's winner against Cardiff in the 2008 FA Cup final?", "Kanu"),
        ("How did Manchester United beat Spurs in the 2009 League Cup final?", "On penalties"),
        ("Manchester United's 2009 title equalled Liverpool's record of how many league titles?", "18"),
        ("How many points were deducted from Portsmouth in 2009–10 for going into administration?", "Nine"),
        ("How many second-half goals did Jermain Defoe score in Tottenham's 9–1 win in November 2009?", "Five"),
    ]),
    ("Round three: the 2010s and 2020s", [
        ("Who was Chelsea's caretaker manager when they won the FA Cup and the Champions League in 2012?", "Roberto Di Matteo"),
        ("Which club won the 2013 League Cup, beating Bradford 5–0 in the final?", "Swansea City"),
        ("Which goal-line technology system was first used in the Premier League in 2013–14?", "Hawk-Eye"),
        ("Which club beat Liverpool 6–1 on the final day of the 2014–15 season?", "Stoke City"),
        ("Which Chelsea midfielder was named Player of the Season in 2016–17?", "N'Golo Kanté"),
        ("At which ground did a Premier League record crowd of 83,222 watch Tottenham beat Arsenal?", "Wembley"),
        ("Which Fulham player became the youngest in Premier League history, aged 16 years and 30 days?", "Harvey Elliott"),
        ("Which storm forced the postponement of Manchester City v West Ham in February 2020?", "Storm Ciara"),
        ("Which Spurs forward became the first Asian player to win the Golden Boot?", "Son Heung-min"),
        ("Who was the first Australian to manage in the Premier League?", "Ange Postecoglou"),
    ]),
]

SLUG = "football-general-knowledge-quiz"
TITLE = "Football General Knowledge Quiz: 30 Questions and Answers"
DESC = ("A free football general knowledge quiz: 30 questions and answers on England's top "
        "flight from 1992 to today. Tap to reveal each answer and keep score.")

QUIZ_CSS = """<style>
.quiz p{max-width:72ch}.quiz .lede{color:var(--muted)}
.quiz h2{font-family:var(--display);font-weight:500;font-size:22px;margin:26px 0 8px}
.quiz ol{padding-left:1.4em;margin:0}.quiz li{margin:0 0 14px;max-width:72ch}
.quiz details{margin-top:4px}.quiz summary{cursor:pointer;color:var(--green);font-weight:600;width:max-content}
.quiz details p{margin:4px 0 0;font-weight:700}
.quiz .more a{color:var(--green);font-weight:600}
</style>"""


def build(site, fonts, style):
    n = 0
    body = []
    for heading, qs in ROUNDS:
        items = []
        for q, a in qs:
            n += 1
            items.append(f'<li value="{n}">{html.escape(q)}<details><summary>Show answer</summary>'
                         f'<p>{html.escape(a)}</p></details></li>')
        body.append(f'<h2>{html.escape(heading)}</h2>\n<ol>{"".join(items)}</ol>')
    url = f"{site}/{SLUG}/"
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="{html.escape(DESC)}">
<link rel="canonical" href="{url}">
<meta property="og:url" content="{url}">
<meta property="og:title" content="{html.escape(TITLE)}">
<meta property="og:description" content="{html.escape(DESC)}">
<meta property="og:image" content="{site}/pins/daily.png">
<title>{html.escape(TITLE)}</title>
{fonts}
{style}
{QUIZ_CSS}
</head>
<body>
<div class="wrap">
  <header><h1 class="brand"><a href="/" style="color:inherit;text-decoration:none">Injury Time <span>Puzzles</span></a></h1></header>
  <main class="quiz">
    <h1 style="font-family:var(--display);font-weight:500;font-size:30px;margin:10px 0">Football general knowledge quiz</h1>
    <p class="lede">Thirty football general knowledge questions on England's top flight, from the first
    Premier League season in 1992–93 to the present day. Three rounds, one for each era. Have a go,
    then tap "Show answer" to check. A score of 20 or more is very good going.</p>
    {"".join(body)}
    <h2>Fancy more?</h2>
    <p class="more">There is a free 12-clue sports crossword every day on the <a href="/">home page</a>,
    and a crossword for <a href="/puzzles/">every top-flight season since 1992</a>. For a whole book of
    football crosswords and quizzes, try <a href="https://www.amazon.co.uk/dp/B0HMP3HHW5?tag=dermcarm089-21"
    target="_blank" rel="noopener sponsored">Top-Flight Football Crosswords: England</a>, printed by Amazon.</p>
  </main>
</div>
</body>
</html>
"""
