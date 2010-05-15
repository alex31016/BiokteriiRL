~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                             GENERAL INFORMATION
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Implementation of Reinforcement Learning (QLearning) using Biokterii
Code available at http://github.com/alex31016/BiokteriiRL

Rafael Santos A01161734@itesm.mx
Jonathan Valle A01161110@itesm.mx
Alejandro Morales A01161376@itesm.mx 

Developed for our Machine Learning Course by Dr. Jorge Ramírez Uresti
Tecnológico de Monterrey, Campus Estado de México
May 2010.


General Use:

Execute main.exe and the agent will start learning according to its QTable.
You can modify the initial reinforcement table located on ./resources/rtable.csv
that file can be edited on any text editor.
The general structure of that table is:

Current State, Action, Next State, Reinforcement
A,AR,A,100

Feel free to modify this table and change the virus behaviour.

You can acces the current QTable at any time from the menu "Actions"