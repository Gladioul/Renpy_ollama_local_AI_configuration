## ¿Dreaming to create a ChatBot using Ren'py as your UI?

This ren'py project is a functional concept of how using ren'py connected to ollama.cpp could bring a nice full local Chatbot, this repo provides a project of renpy to customize it and the project build.

##  Set up

###  Option A:
1. Download only the releases .zip, they are on the Releases section in the right. Download only the one of your SO (Only tested on Windows)
2. Download ollama and download the model via ollama
3. Run the model on Ollama 
4. Start the .exe
5. Start the game, and YOU GOT IT

### Option B:
1. Download this project and move to your folder where the other renpy projects are stored or create a new one and overwrite it with this one (Other way is only changing the scrypt.rpy file)
   To download you can go to the button Code-> Download Zip or use git.
3. Download ollama and download the model via ollama
4. Run the model on Ollama 
5. Launch the project
6. Start the game, and YOU GOT IT
   
## Important settings

### Choosing model: 

This project is using  gemma3:1b, provides good performance for 'low' system requirements, but you can pick other model. Remember to change the 8 line on scrypt.rpy with the name of the model


## I have all set up ¿How I run it?

You have to start ollama.exe (If you don't have config to boot on start)

Use cmd to run the model (Example: ollama run gemma3:1b)
![Ollama](pics/Ollama.png)

The run the renpy project

## Results

![Start](pics/Start.png)
![Input](pics/Input.png)
![Pics](pics/Output.png)




## Customaization 

You can add a 'base prompt' by addig the tokens via code on scrypt.rpy it can give you:
* Personality for your character
* Limit the number of words of the response (It is already implemented to fit in the chatter box

You can do some settings on the output tokens and choose your model on the scrypt.rpy

## Tips and Tricks

-Use auto to avoid spaming clicks to know when the response has been served
-Put the auto setting bar below mid to get a more fluid conversation


## ¿Future updates?
-Translating text on the screenshoots to English and some text that is not in English

-Do some cleaning on the Files 

-Add some style to the program (It's pretty rough):
Image for the girl
Not use the default UI
Beurify the menu

-Program that if the response is too big for the dialogue box, put it on the next dialogue box (Feaseable) **Done**


-Upgrading this Wiki, after more testing

-Integrate transformers or ollama on the renpy project to have a stand alone build to use locally

-Better response time, this can be tough I see other webUI struggling with this

-Add more AI tools (This one is greedy)

## Trouble shoothing

-Waiting Feedback!!!!


##  Related Projects:

https://github.com/Calandiel/llama-renpy/blob/master/script.rpy