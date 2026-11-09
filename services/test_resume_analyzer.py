
from pprint import pprint

from resume_analyzer import analyze_resume


sample_resume = """
Alex Morgan
Junior Software Developer

Education:
Bachelor's degree in Computer Science.

Experience:
Completed a university project building a task
management application using Python and SQL.

Skills:
Python, SQL, Git, problem solving.

Project:
Developed database queries and implemented basic
application features as part of a student team.
"""

analysis = analyze_resume(sample_resume)

pprint(analysis)
