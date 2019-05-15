# STRESS:
#FROM python:3
#COPY requirements.txt .
#COPY source ./source/
#COPY start.py ./
#RUN pip install -r ./requirements.txt
#RUN apt install mysqldump
#CMD ["python3", "start.py", "stress"]

# FAKING TAG MOVEMENT ON FLOOR SET IN PATHS
FROM python:3
COPY requirements.txt .
COPY source ./source/
COPY paths ./paths/
COPY start.py ./
RUN pip install -r ./requirements.txt
CMD "python3" "start.py" "path" "paths/11999.json" "paths/12000.json"
