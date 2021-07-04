from django.shortcuts import render, redirect
from .models import Desease, imageSearch
from django.db.models import Q
from googletrans import Translator
import speech_recognition as sr
from selenium import webdriver
from bs4 import BeautifulSoup
import cloudscraper
import html5lib
import numpy as np
import cv2
import tensorflow as tf
from tensorflow import keras
import os
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from .form import CreateUserFrom, DiseaseForm
from django.contrib.auth import authenticate, login, logout
from .decorator import  unauthenticated_user, allowed_user

useless_words = [
    "About","Above","According to","Across","After","Against","Ahead of","Along","Amidst","Among","Amongst","Apart from",
    "Around","As","As far as","As well as","Aside from","At","Barring","Because of","Before","Behind","Below","Beneath","Beside","Besides","Between",
    "Beyond","By","By means of","Circa","Concerning","Despite","Down","Due to","During","In","In accordance with","In addition to","In case of",
    "In front of","In lieu of","In place of","In spite of","In to","Inside","Instead of","Into","Except","Except for","Excluding","For","Following",
    "From","Like","Minus","Near","Next","Next to","Past","Per","Prior to","Round","Since","Off","On","On account of","On behalf of","On to",
    "On top of","Onto","Opposite","Out","Out from","Out of","Outside","Over","Owing to","Plus","Than","Through","Throughout","Till","Times",
    "To","Toward","Towards","Under","Underneath","Unlike","Until","Unto","Up","Upon","Via","With","With a view to","Within","Without","a","an","the",
]
model = keras.models.load_model(os.path.join(settings.BASE_DIR,'trainned_desease.model'))

@allowed_user(allowed_roles = ['admin'])
def homepage(request):
    return render(
        request, 
        "main/home.html", 
        {"desease":Desease.objects.all}
    )

def desease(request, pk):
    d = Desease.objects.get(id = pk)

    return render(
        request,
        "main/desease.html",
        {"desease": d}
    )

#searcing logic
def search(request):
    query = request.GET['quary']

    initital_query = query
    query1 = Translator(service_urls=['translate.googleapis.com']).translate(text=query, dest='en')

    this_language = query1.src
    query = query1.text
    
    search_scrapper_res, ob = search_scrapper(query)
    request.session['passing'] = ob
    
    res = list(set(Desease.objects.filter(
        Q(Disease_name__icontains=query) | 
        Q(Disease_description__icontains=query) |
        Q(Disease_symptoms__icontains=query) |
        Q(Disease_remidies__icontains=query) 
    )))

    if(this_language != 'en'):
        for i in res:
            i.Disease_name = Translator(service_urls=['translate.googleapis.com']).translate(text=i.Disease_name, dest=this_language).text
        for i in search_scrapper_res:
            i[0] = Translator(service_urls=['translate.googleapis.com']).translate(text=i[0], dest=this_language).text
    return render(request, "main/search.html", {"found_desease":res, "query":initital_query, "useless_words":useless_words, "found_scrap": search_scrapper_res})

def voice_search(request):
    r2 = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r2.listen(source)
        try:
            get = r2.recognize_google(audio)
            s1 = Translator(service_urls=['translate.googleapis.com']).translate(text=get, dest='en')
            
            this_language = s1.src
            s = s1.text
            s = s.split()
            res = []
            
            for i in s:
                if(i not in useless_words):
                    res+=list(Desease.objects.filter(
                        Q(Disease_name__icontains=i) | 
                        Q(Disease_description__icontains=i) |
                        Q(Disease_symptoms__icontains=i) |
                        Q(Disease_remidies__icontains=i) 
                    ))

            res = list(set(res))
            if(this_language != 'en'):
                for i in res:
                    i.Disease_name = Translator(service_urls=['translate.googleapis.com']).translate(text=i.Disease_name, dest=this_language).text

            return render(request, "main/search.html", {"found_desease":res, "query":get})
        except:
            pass

def about(request):
    return render(request, "main/about.html")

def desease_scrap(request, pk):
    store = request.session['passing']
    out = urlOpener_scrapper(store[int(pk)])
    return render(request, "main/scrap_out.html", {"out": out})

def camera_search(request):
    p = request.FILES.get('image')
    res = []
    query = ""
    if(p != None):
        img_search = imageSearch(uploaded_image = p)
        p._set_name("test.jpg")
        if os.path.exists(os.path.join(settings.BASE_DIR, "static/images/test.jpg")):
            os.remove(os.path.join(settings.BASE_DIR, "static/images/test.jpg"))
        name_of_doc = p._get_name()
        img_search.save()
        query = disease_identifier(name_of_doc)
        search_scrapper_res, ob = search_scrapper(query)
        request.session['passing'] = ob

        res = list(set(Desease.objects.filter(
        Q(Disease_name__icontains=query) | 
        Q(Disease_description__icontains=query) |
        Q(Disease_symptoms__icontains=query) |
        Q(Disease_remidies__icontains=query) 
    )))

    
    if(request.POST):
        return render(request, "main/search.html", {"found_desease":res, "query":query,"found_scrap": search_scrapper_res})
    else:
        return render (request, "main/camera_search.html")


#login logic
def register(request):
    if request.user.is_authenticated:
        return redirect("homepage")
    form = CreateUserFrom()

    if request.method == "POST":
        form = CreateUserFrom(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect("homepage")

    return render(request, "main/register.html", {'form':form})

@unauthenticated_user
def loginpage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('homepage')

    return render(request, "main/login.html")

def logout_request(request):
    logout(request)
    return redirect('homepage')


#ml_logic
def disease_identifier(inp):
    CATAGORIES = [
        'Apple___Apple_scab',
        'Apple___Black_rot',
        'Apple___Cedar_apple_rust',
        'Apple___healthy',
        'Blueberry___healthy',
        'Cherry_(including_sour)___healthy',
        'Cherry_(including_sour)___Powdery_mildew',
        'Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot',
        'Corn_(maize)___Common_rust_',
        'Corn_(maize)___healthy',
        'Corn_(maize)___Northern_Leaf_Blight',
        'Grape___Black_rot',
        'Grape___Esca_(Black_Measles)',
        'Grape___healthy',
        'Grape___Leaf_blight_(Isariopsis_Leaf_Spot)',
        'Orange___Haunglongbing_(Citrus_greening)',
        'Peach___Bacterial_spot',
        'Peach___healthy',
        'Pepper,_bell___Bacterial_spot',
        'Pepper,_bell___healthy',
        'Potato___Early_blight',
        'Potato___healthy',
        'Potato___Late_blight',
        'Raspberry___healthy',
        'Soybean___healthy',
        'Squash___Powdery_mildew',
        'Strawberry___healthy',
        'Strawberry___Leaf_scorch',
        'Tomato___Bacterial_spot',
        'Tomato___Early_blight',
        'Tomato___healthy',
        'Tomato___Late_blight',
        'Tomato___Leaf_Mold',
        'Tomato___Septoria_leaf_spot',
        'Tomato___Spider_mites Two-spotted_spider_mite',
        'Tomato___Target_Spot',
        'Tomato___Tomato_mosaic_virus',
        'Tomato___Tomato_Yellow_Leaf_Curl_Virus'
    ]
    
    DATA = os.path.join(settings.BASE_DIR,"static/images/"+inp)
    img_arr = cv2.imread(DATA, cv2.COLOR_BGR2HSV)
    new_arr = cv2.resize(img_arr, (250, 250))
    new_arr = np.array(new_arr).reshape(-1, 250, 250, 3)
    predicted = np.argmax(model.predict(new_arr))
    output = CATAGORIES[predicted]
    removed__ = " ".join(output.split("__"))
    removed_ = " ".join(output.split("_"))
    return(removed_)


#scrapping logic
def search_scrapper(inp):
    store = []
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument(f'user-agent={user_agent}')
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument("--disable-extensions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--start-maximized")
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    
    
    inp = "%20".join(inp.split())
    url = "https://www.gardeningknowhow.com/search?q="+inp
    print(url)
    driver.get(url) #navigate to the page
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    out = soup.find_all('a', {'class', 'gs-title'})
    search_res = []
    old_i = ''
    count=-1
    for i in out:
        count += 1
        store.append(str(i).split()[2][13:-1])
        if(old_i == i):
            continue
        old_i = i
        b = i.get_text()
        if(b == ' '):
            break

        
        search_res.append([b, str(count)])
    return(search_res, store)

def urlOpener_scrapper(url):
    scraper = cloudscraper.create_scraper()
    htmlContent = scraper.get(url).content
    soup = BeautifulSoup(htmlContent, 'html.parser')
    paragraph = soup.find('div', id="main-art")
    tot = []
    head = []
    para = []
    for i in paragraph.contents:
        if(str(i)[1:3] == "h2"):
            tot.append([head, para])
            head = []
            para = []
            head.append(i)
        else:
            para.append(i)
    tot.append([head,para])
    
    output = {}
    for i in tot[1:]:
        heading = i[0][0].get_text()
        sub_out = []
        for j in i[1]:
            soup = BeautifulSoup(str(j), "html.parser")
            sub_out.append(soup.get_text().strip())

        output[heading] = sub_out
    return output
    


@allowed_user(allowed_roles = ['admin'])
def update_database(request):
    form = DiseaseForm()
    if request.method == "POST":
        form = DiseaseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("homepage")
    return render(request, "main/update_database.html", {'form':form})

@allowed_user(allowed_roles = ['admin'])
def change_database(request, pk):
    disease = Desease.objects.get(id = pk)
    form = DiseaseForm(instance=disease)
    if request.method == "POST":
        form = DiseaseForm(request.POST, instance=disease)
        if form.is_valid():
            form.save()
            return redirect("homepage")
    return render(request, "main/update_database.html", {'form':form})

@allowed_user(allowed_roles = ['admin'])
def delete_database(request, pk):
    disease = Desease.objects.get(id = pk)
    if request.method == "POST":
        disease.delete()
        return redirect("homepage")

    return render(request, "main/delete_confirmation.html", {'disease':disease, "pk":pk})


def user_page(request):
    return render(request, "main/user.html", {"desease":Desease.objects.all})