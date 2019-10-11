# DataVizTrials

### VirtualEnv Set Up
The venv has been .gitignore'd, so all of the dependencies have been frozen into requirements.txt. To rebuild a mirrored Virtualenv, at the root of your project directory run the following:
'''' bash
$ python3 -m venv env
$ pip install -r requirements.txt
''''

If you download any additional packages through pip for the project, please include them in the requirements.txt by running: 
'''' bash
$ pip freeze > "requirements.txt"
''''
