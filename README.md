# pyBackup

On my continued goal of looking for projects to automated right now I have made one that I use very frequently, backups. My normal backup routine is using rclone to sync folders with different arguments depending on the folder. 

And right as I was typing out this summary I realized that I had not really completed my goal so I stopped and re-worked it to then actually take different arguments depending on the folder. 

So with that said I have 2 versions available ```pyBackup.py``` which is the first version I made that only has one set of arguments for all folders and no other options. The 2nd version ```pyBackup.2.0.py``` includes the additional arguments. There is HOME_ARG which could be for any other folder than home but that is what I am using it for primarily, and then there is just ARGS which you can put the main ones you will use on all and the HOME for the folder you want separately. 

They are both setup to be used as cronjobs with no input required, it will log out to a pyBackup.log in the same dir of the script. 