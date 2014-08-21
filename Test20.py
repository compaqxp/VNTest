#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
	import pygame
	import json
	import zipfile
	import io
	import pickle
	import re
	import sys
	import conf
	import webbrowser
	import pygame._view #This line is required if you expect to build an exe and have it work. See changelog TEST020.
	from time import sleep, strftime
	from itertools import chain
except ImportError, message:
    print "Unable to load module. {}".format(message)
    raise SystemExit

pygame.init()

class TextRectException:
    def __init__(self, message = None):
        self.message = message
    def __str__(self):
        return self.message

##############################################################################
#Functions for rendering text. It's important to note TextRectRender is NOT  #
#my code. At some point I should replace it. Maybe tomorrow, or the next day #
#because I now understand how to do it.                                      #
##############################################################################      
  
def TextRectRender(string, font, rect, textcolour, backgroundcolour, justification=0):
    finallines = []

    requestedlines = string.splitlines()

    for requestedline in requestedlines:
        if font.size(requestedline)[0] > rect.width:
            words = requestedline.split(' ')
            for word in words:
                if font.size(word)[0] >= rect.width:
                    raise TextRectException, "The word " + word + " is too long to fit in the rect passed."
            accumulatedline = ""
            
            for word in words:
                test_line = accumulatedline + word + " "   
                if font.size(test_line)[0] < rect.width:
                    accumulatedline = test_line 
                else: 
                    finallines.append(accumulatedline) 
                    accumulatedline = word + " " 
            finallines.append(accumulatedline)
        else: 
            finallines.append(requestedline) 

    surface = pygame.Surface(rect.size, pygame.SRCALPHA) 
    surface.fill((150, 150, 150, 0))

    accumulatedheight = 0 
    for line in finallines: 
        if accumulatedheight + font.size(line)[1] >= rect.height:
            raise TextRectException, "Once wrapped, the text string was too tall to fit in the rect."
        if line != "":
            tempsurface = font.render(line, 1, textcolour)
            if justification == 0:
                surface.blit(tempsurface, (0, accumulatedheight))
            elif justification == 1:
                surface.blit(tempsurface, ((rect.width - tempsurface.get_width()) / 2, accumulatedheight))
            elif justification == 2:
                surface.blit(tempsurface, (rect.width - tempsurface.get_width(), accumulatedheight))
            else:
                raise TextRectException, "Invalid justification arg: " + str(justification)
        accumulatedheight += font.size(line)[1]

    return surface

def TextRender(text, colour, size, fontfile): #Function for rendering character and story text
	font = pygame.font.Font("fonts/{}.ttf".format(fontfile), size)
	textrender = font.render(text, 1, (colour))
	return textrender

###############################################################	
#Functions loading data from zips and getting parsed json data#
###############################################################

def StoryData(table, value): #Parse story json file
	parsed_json = json.loads(conf.storydata)
	json_data = parsed_json[table][value]
	return json_data
  
def LoadFromZip(location, name, filetype): #Load images, music and other content from zip file
	zipcontents = archive.read('{}/{}.{}'.format(location, name, filetype))
	bytesio = io.BytesIO(zipcontents) #Pygame won't accept files straight from zip. Do this so it can use them.
	return bytesio

###############################################################################	
#Functions for manipulating characters, backgrounds and other on screen things#
###############################################################################
	
def CharMove(x, y): #Moves char or something
	characterrect.move_ip(x, y)
	return
	
def BGLoad(bgtable): #Loads background image
	global background, backgroundrect
	background = pygame.image.load(LoadFromZip(conf.backgrounddir, StoryData(bgtable, "background"), "jpg"))
	backgroundrect = background.get_rect()
	return
	
def CharLoad(char): #Loads character image
	global characterimage, characterrect
	characterimage = pygame.image.load(LoadFromZip(conf.characterdir, char, "png"))
	characterrect = characterimage.get_rect()
	CharMove(0, 0)
	return
	
def VideoPlay(videofile): #Plays videos
	try:
		introvideo = pygame.movie.Movie('{}/{}.vnv'.format(conf.avdir, videofile))
		introscreen = pygame.Surface(introvideo.get_size()).convert()
		introvideo.set_display(introscreen)
		introvideo.play()
		playing = True
		while playing:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					introvideo.stop()
					playing = False
					done = True
				
			screen.blit(introscreen,(0,0))
			pygame.display.update()
			click.tick(int(conf.config.get('settings', 'videofps')))
			if introvideo.get_busy() == False:
				playing = False
				
	except:
		LogError('Video file ({}.vnv), not found!'.format(videofile))
		playing = False
	return

#################################
#Functions for controlling audio#
#################################

def StartAudio(audiofile): #Starts music playing, can be called at any point to change audio.
	try:
		pygame.mixer.init()
		pygame.mixer.music.load("{}/{}.vnm".format(conf.avdir, audiofile))
		pygame.mixer.music.set_volume(float(conf.config.get('settings', 'volume')))
	except:
		LogError('Audio file ({}/{}.vnm), not found!'.format(conf.avdir, audiofile))
		raise SystemExit, 'There was an error. Check errorlog.txt for more info.'
	return
	
def MuteSound(audio):#Mutes game audio.
	if audio == True:
		pygame.mixer.music.pause()
		audio = False
	elif audio == False:
		pygame.mixer.music.unpause()
		audio = True
	return audio

###########################################################	
#Functions displaying ingame menus/debug data/story scenes#
###########################################################

def MainMenu(): #Display main menu title/options.
	global menu, done, currentscene, audio, storytext, character, table
	if mainmenurendered == False:
		#Main menu BG
		mainmenubg = pygame.image.load(LoadFromZip(conf.backgrounddir, "mainmenu", "jpg"))
		mainmenubgrect = mainmenubg.get_rect()
		screen.blit(mainmenubg, mainmenubgrect)
		
		#Game title
		screen.blit(TextRender(conf.mmtText, conf.white, conf.mmtSize, 'titles'), conf.mmtLoc)
		screen.blit(TextRender(conf.devText, conf.white, conf.devSize, 'titles'), conf.devLoc)
		screen.blit(TextRender(conf.copyText, conf.black, conf.copySize, 'titles'), conf.copyLoc)
		
		#Load images for buttons
		playbtn = pygame.image.load(LoadFromZip(conf.uidir, "btn_play", "png")).convert_alpha()
		loadbtn = pygame.image.load(LoadFromZip(conf.uidir, "btn_load", "png")).convert_alpha()
		infobtn = pygame.image.load(LoadFromZip(conf.uidir, "btn_info", "png")).convert_alpha()
		optionsbtn = pygame.image.load(LoadFromZip(conf.uidir, "btn_options", "png")).convert_alpha()
		quitbtn = pygame.image.load(LoadFromZip(conf.uidir, "btn_quit", "png")).convert_alpha()
		
		#Blit buttons
		playbtnren = screen.blit(playbtn, conf.playLoc)
		loadbtnren = screen.blit(loadbtn, conf.loadLoc)
		optionsbtnren = screen.blit(optionsbtn, conf.optionLoc)
		infobtnren = screen.blit(infobtn, conf.infoLoc)
		quitbtnren = screen.blit(quitbtn, conf.quitLoc)
		
		#Simple mouse over animations for buttons
		if playbtnren.collidepoint(pos):
			playbtnmouseover = pygame.image.load(LoadFromZip(conf.uidir, "btn_play_mouseover", "png")).convert_alpha()
			screen.blit(playbtnmouseover, conf.playLoc)
				
		elif loadbtnren.collidepoint(pos):
			loadbtnmouseover = pygame.image.load(LoadFromZip(conf.uidir, "btn_load_mouseover", "png")).convert_alpha()
			screen.blit(loadbtnmouseover, conf.loadLoc)
				
		elif optionsbtnren.collidepoint(pos):
			optionsbtnmouseover = pygame.image.load(LoadFromZip(conf.uidir, "btn_options_mouseover", "png")).convert_alpha()
			screen.blit(optionsbtnmouseover, conf.optionLoc)
				
		elif infobtnren.collidepoint(pos):
			infobtnmouseover = pygame.image.load(LoadFromZip(conf.uidir, "btn_info_mouseover", "png")).convert_alpha()
			screen.blit(infobtnmouseover, conf.infoLoc)
				
		elif quitbtnren.collidepoint(pos):
			quitbtnmouseover = pygame.image.load(LoadFromZip(conf.uidir, "btn_quit_mouseover", "png")).convert_alpha()
			screen.blit(quitbtnmouseover, conf.quitLoc)
		
		for event in pygame.event.get():
			if event.type == pygame.MOUSEBUTTONDOWN: #If mouse if clicked see if it clicked a button, if it did do stuff.
				
				if playbtnren.collidepoint(pos):  #Starts fresh game
					menu = False
					pygame.event.clear()
					if fromgame == True:
						currentscene = "a"
					
				elif loadbtnren.collidepoint(pos): #Load previous save
					with open('dat/savefile') as f:
						data = pickle.load(f)
					table = data
					storytext = StoryData(table, "dialog")
					character = StoryData(table, "character")
					menu = False
					currentscene = "a"
					
				elif infobtnren.collidepoint(pos): #Open up webpage with info. This should maybe at some point open about about window.
					webbrowser.open('http://www.reddit.com/u/compaqxp')
					
				elif quitbtnren.collidepoint(pos): #Close the game
					done = True
					
			elif key[pygame.K_m]: #Audio toggle. User can press M key to pause or unpause	
				MuteSound(audio)
				audio = MuteSound(audio)
				
			elif (event.type == pygame.QUIT) or (key[pygame.K_q]): #Shortcut for quiting game. Exits right away
				done = True
	else:
		pass
	return 
	
def ShowScene(): #This is the code for showing a scene in game. This get's called a lot.
	global data, currentscene, ingamesavebtnren, ingamequitbtnren, ingamemutebtnren
	#Load textbox overlay
	textbox = pygame.image.load(LoadFromZip(conf.uidir, "textbox", "png"))
	textboxrect = textbox.get_rect()
	
	#Load BG and Character images
	BGLoad(table)
	CharLoad(StoryData(table, "characterimage"))
	
	#Put Bg, Char, Textbox, char name and scene text on screen
	screen.blit(background, backgroundrect)
	screen.blit(characterimage, characterrect)
	screen.blit(textbox, textboxrect)
	screen.blit(TextRender("{}".format(character), conf.black, conf.charactername, 'main'), conf.charnameLoc)

	charactertextbox = pygame.Rect((119, 474, 850, 565))
	rendered_text = TextRectRender(storytext, regularfont, charactertextbox, (0, 0, 0), (191, 191, 191, 150), 0)
	screen.blit(rendered_text, charactertextbox.topleft)
	
	#Load in game buttons
	ingamesavebtn = pygame.image.load(LoadFromZip(conf.uidir, "over_btn_save", "png")).convert_alpha()
	ingamequitplay = pygame.image.load(LoadFromZip(conf.uidir, "over_btn_quit", "png")).convert_alpha()
	ingamemutebtn = pygame.image.load(LoadFromZip(conf.uidir, "over_btn_soundon", "png")).convert_alpha()
	
	#Display in game buttons
	ingamesavebtnren = screen.blit(ingamesavebtn, conf.saveLoc)
	ingamequitbtnren = screen.blit(ingamequitplay, conf.ingamequitLoc)
	ingamemutebtnren = screen.blit(ingamemutebtn, conf.soundLoc)

	#Set other stuff
	data = table
	currentscene = table
	DebugInfo()
	return
	
def DebugInfo(): #Puts Debug info on screen if DebugMode is set true in config.sec
	if conf.debug == True:
		charname = re.sub('[<>]', '', character)
		screen.blit(TextRender('CS: {}'.format(currentscene), conf.red, 16, 'debug'), (10, 10))
		screen.blit(TextRender('CC: {}'.format(charname), conf.red, 16, 'debug'), (10, 25))
		screen.blit(TextRender('DN: {}'.format(done), conf.red, 16, 'debug'), (10, 40))
		screen.blit(TextRender('DM: {}'.format(devmode), conf.red, 16, 'debug'), (10, 55))
		screen.blit(TextRender('AP: {}'.format(pygame.mixer.music.get_busy()), conf.red, 16, 'debug'), (10, 70))
		screen.blit(TextRender('AM: {}'.format(audio), conf.red, 16, 'debug'), (10, 85))
		screen.blit(TextRender('AL: {}'.format(conf.config.get('settings', 'volume')), conf.red, 16, 'debug'), (10, 100))
	else:
		pass
	return

#############################
#Other Less used functions  #
#############################
	
def LogError(error): #Used for logging some simple errors, mostly to do with files not being found.
	time = strftime("%d/%m/%Y %H:%M:%S")
	errorfile = open('errorlog.txt', 'a')
	errorfile.write('{}: {}\n'.format(time, error))
	errorfile.close()
	return

def StartWindow(): #Set window size, title and key repeat rate. Only ever gets used once when game is opened.
	global screen, click	
	if conf.fullscreen == True:
		screen = pygame.display.set_mode(conf.winsize,pygame.FULLSCREEN)
	else:
		screen = pygame.display.set_mode(conf.winsize)
	pygame.display.set_caption(conf.winText)
	pygame.key.set_repeat(100,69)
	click = pygame.time.Clock()
	return
	
try: #Try to open zip file with game images and content, otherwise log an error and quit.
	archive = zipfile.ZipFile(conf.assets, "r")
except:
	LogError('Assest archive ({}), not found!'.format(conf.config.get('files', 'assets')))
	raise SystemExit, 'There was an error. Check errorlog.txt for more info.'

#Open window and load audio
StartWindow()
StartAudio('music')

#Set fonts
regularfont = pygame.font.Font(conf.regularfont, conf.storysize)
debugfont = conf.debug

#Inital json data to grab. We need this to start the story.
table = conf.initaltable
bgtable = table
character = StoryData(table, "character")
storytext = StoryData(table, "dialog") 

#Load first bg/char to the screen and load inital music
background = pygame.image.load(LoadFromZip(conf.backgrounddir, StoryData(table, "background"), "jpg"))
backgroundrect = background.get_rect()
characterimage = pygame.image.load(LoadFromZip(conf.characterdir, StoryData(table, "characterimage"), "png"))
characterrect = characterimage.get_rect()
currentscene = "A" #This is just garbage, this variable gets changed later.
StartAudio('music')

#Set inital variables for the main loop
done = False
audio = True
fromgame = False
mainmenurendered = False

#Check if devmode is on. If it is skip the intro video.
if conf.devmode == False:
	menu = False
	intro = True
	
elif conf.devmode == True:
	menu = True
	intro = False
	pygame.mixer.music.play()
	
#Loop for the intro, this only ever needs to play once so it's not in the main loop
while intro == True:
	VideoPlay('intro')
	pygame.mixer.music.play()
	intro = False
	menu = True

#Main loop
while done == False:
	key = pygame.key.get_pressed()
	pos = pygame.mouse.get_pos()
	
	if menu == True: #This starts main menu. It should always come up after the intro
		MainMenu()
		mainmenurendered = False #This line *was* used to keep the main menu from using too much CPU. At the moment it does nothing.
		DebugInfo()
				
	elif menu == False: #This is the code for the main game, when menu == false we can begin
		if table != currentscene: #Put char, bg and text on screen unless the scene has not changed in which case do nothing.
			ShowScene()
		else:
			pass

		if pygame.mixer.music.get_busy() == False: #If music has finished playing start it again
			pygame.mixer.music.play()
	
		if StoryData(table, "end") == "True": #If the story is done we play credits and return to main menu.
			table = "scene1"
			storytext = StoryData(table, "dialog")
			character = StoryData(table, "character")
			VideoPlay('credits')
			intro = False
			playing = False
			done = False
			menu = True
			mainmenurendered = False

		for event in pygame.event.get(): #Get any event (keybo/mouse presses)
			if event.type == pygame.QUIT:
				done = True

			#If the right/space key is pressed get everything set up to advance to next scene
			elif (key[pygame.K_RIGHT]) or (key[pygame.K_SPACE]):
				currentscene = table
				table = StoryData(table, "nextscene")
				storytext = StoryData(table, "dialog")
				character = StoryData(table, "character")
				
			elif key[pygame.K_LEFT]: #If user presses left arrow go back to previous scene
				currentscene = table
				table = StoryData(table, "lastscene")
				storytext = StoryData(table, "dialog")
				character = StoryData(table, "character")
				
			elif key[pygame.K_m]: #Audio toggle. User can press M key to pause or unpause	
				MuteSound(audio)
				audio = MuteSound(audio)
				
			elif key[pygame.K_q]: #Shortcut for quiting game. Exits right away, should ask for confirmation.
				done = True
			
			elif key[pygame.K_ESCAPE]: #If user presses esc go back to the main menu.
				menu = True
				fromgame = True
				mainmenurendered = False
				bgtable = conf.initaltable
			
			elif event.type == pygame.MOUSEBUTTONDOWN: #This is used the the buttons on the side of the screen in game.
				pos = pygame.mouse.get_pos()
				if ingamesavebtnren.collidepoint(pos): #save game
					with open('dat/savefile', 'w') as f:
						pickle.dump(data, f)
						
				elif ingamemutebtnren.collidepoint(pos): #mute audio
					MuteSound(audio)
					audio = MuteSound(audio)
					
				elif ingamequitbtnren.collidepoint(pos): #quit game
					done = True
				
			
	pygame.display.flip() 
	click.tick(int(conf.config.get('settings', 'gamefps')))

pygame.quit()
