import ConfigParser

#Dev settings
devmode = False
debug = False

#Read usereditable config file 
config = ConfigParser.ConfigParser()
config.read('dat/config.sec')

#File tpye directory info
backgrounddir = 'bg'
characterdir = 'char'
avdir = 'av'
uidir = 'ui'
otherdir = ''

#Window settings
winsize = (1024, 576)
fullscreen = False

#Font locations/sizes
charactername = 18
storysize = 18
menubuttons = 22

storycontent = 'dat/store.sty'
savefile = 'dat/savefile'
regularfont = 'fonts/main.ttf'
debugfont = 'fonts/debug.ttf'

#Open and read story contents from json file
storydataread = open('dat/store.sty', 'r')
storydata = storydataread.read()

#Location for main menu buttons
playLoc = (25, 200)
loadLoc = (25, 260)
optionLoc = (25, 320)
infoLoc = (25, 380)
quitLoc = (25, 440)

#Main menu text, size and location
mmtLoc = (25, 5)
devLoc = (25, 50)
copyLoc = (645, 588)
mmtSize = 46
devSize = 16
copySize = 10
winText = 'KNPB Test 0.20'
mmtText = 'KNPB'
devText = 'Test 0.20'
copyText = '(C) 2014 Connor Oliver'

#Story text render settings
charnameLoc = (125, 454)

#Ingame button locations
saveLoc = (991,472)
soundLoc = (991, 504)
ingamequitLoc = (991, 538)

#Colours
white = (255,255,255)
black = (0,0,0)
red = (235,16,16)

#File locations
assets = 'dat/ast.pne'

#JSON info
initaltable = 'scene1'
