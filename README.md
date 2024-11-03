## LaQuiniela of LaLiga

Team members:<br>
Carlos Pablo Villalta López - NIU: 1727276<br>
Jonas Daniel Elzinga - NIU: 1731222<br>
Moritz Marquardt - NIU: 1734959<br>
Oscar Mauricio Cardona Mejia - NIU: 1687394<br>
Raúl Alberto Argüello Cajicá - NIU: 1734898<br>

In this repository a few things can be found.<br>
First of all, an analysis of LaLiga can be found in the reports folder under the name "LaLigaDataAnalysis.html", the analysis was done in a jupyter notebook under the same name which is stored in the analysis folder.<br>
Secondly, a ML model is implemented in the quiniela folder. To find out which model we wanted to use we tried a lot of different things, all of which can be found in the analysis folder where it is stored in the legacy folder. The final choices that to us seemed the right ones were implemented in one final notebook, also stored in the analysis folder under the name "ModelAnalysis.ipynb". This notebook has also been made into a html file which is stored in the reports folder under the same name.<br>

### Repository structure

```
quiniela/
  ├─── analysis/				# Jupyter Notebooks used to explore the data
  │          ...
  ├─── logs/					# Logs of the program are written
  │          ...
  ├─── models/					# The place were trained models are stored
  │          ...
  ├─── quiniela/				# Main Python package
  │          ...
  ├─── reports/					# The place to save HTML / CSV / Excel reports
  │          ...
  ├─── .gitignore
  ├─── cli.py					# Main executable. Entrypoint for CLI
  ├─── README.md
  ├─── requirements.txt			# List of libraries needed to run the project
  └─── settings.py				# General parameters of the program
```

### How to run it
To run the model that we implemented, it is first important to install all the dependencies. This can be done by running the following command in the terminal:
```console
pip install -r requirements.txt
```
After this is done, the model can be trained and tested. To train the model, the following command can be used:
```console
foo@bar:~$ python cli.py train --training_seasons {first year}:{last year}
```
Where {first year} is the first year that you want to train the model on and {last year} is the last year that you want to train the model on, all the seasons in between these years will be included (example, begin year is 2010 and end year is 2012, then the seasons 2010-2011 and 2011-2012 will be used to train). The trained model will then be saved in the models folder.<br>

To then predict the outcome of a matchday, the following command can be used:
```console
foo@bar:~$ python cli.py predict {season} {division} {matchday}
```
Where {season} is the season that you want to predict the outcome of (this time the complete season, so for example 2020-2021), {division} is the division that you want to predict the outcome of and {matchday} is the matchday that you want to predict the outcome of. The prediction will then be printed in the terminal like this:
```console
Matchday 3 - LaLiga - Division 1 - Season 2021-2022
======================================================================
         RCD Mallorca          vs            Espanyol            --> 1
           Valencia            vs             Alavés             --> 1
        Celta de Vigo          vs            Athletic            --> 0
        Real Sociedad          vs            Levante             --> 0
           Elche CF            vs           Sevilla FC           --> 2
          Real Betis           vs          Real Madrid           --> 2
          Barcelona            vs             Getafe             --> 1
           Cádiz CF            vs           CA Osasuna           --> 1
        Rayo Vallecano         vs           Granada CF           --> 0
       Atlético Madrid         vs           Villarreal           --> 1
Model accuracy: 0.40
```
