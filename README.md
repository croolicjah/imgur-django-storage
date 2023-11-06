
# Imgur Django Custom Storage or how to upload images to imgur straitghly from Django
 Custom imgur file storage for django allows you to upload files from your ImageField to imgur.com. So you can use imgur as a remote storage. Integretion is very easy. You don't need huge libraries or stuff you don't mostly don't need. Imgur custom storage works specially with Django 4.2 but support lower versions as well. There is **no need to replace default Django** [`FileSystemStorage`](https://docs.djangoproject.com/en/4.2/ref/files/storage/#django.core.files.storage.FileSystemStorage "django.core.files.storage.FileSystemStorage"). 
## Requirements
All you need is Django of course and [Requests: HTTP for Humans™](https://requests.readthedocs.io/en/latest/). To make possible playing with imgur API you need to collect: 
 - CLIENT ID
 - CLIENT SECRET
 - ACCESS TOKEN
 - REFRESH TOKEN
 
 How to grab it you can find here: https://apidocs.imgur.com/#authorization-and-oauth. And remember, you will find token inside url after authorization.
 ## Setup Django
 First download `imgur_storage.py` to your project for example into django root directory. But you can place this file whereever you want.

![image](https://github.com/croolicjah/imgur-django-storage/assets/8026783/fba96d1b-50c6-49e9-b80c-0e863dfdc975)

Users who works with lower **Django version < 4.2** should unhash the lines in `imgur_storage.py` and comment redudant. After this operation your file should looks like below:

    # unhash below if you are using lower version Django < 4.2
    imgur_access = STORAGES['imgur']['OPTIONS'] <-- this line should be uncommented
        
    @deconstructible
    class ImgurStorage(Storage):
    
    def __init__(self, **kwargs):
    
        # self.CLIENT_ID = kwargs.get("CLIENT_ID")     <-- hash those lines. it's not necessary.
        # self.CLIENT_SECRET = kwargs.get("CLIENT_SECRET")
        # self.CLIENT_USERNAME = kwargs.get("CLIENT_USERNAME")
        # self.ACCESS_TOKEN = kwargs.get("ACCESS_TOKEN")
        # self.REFRESH_TOKEN = kwargs.get("REFRESH_TOKEN")
        # self.base_api_url = kwargs.get('base_api_url')
    
        # unhash code below if you are using lower version Django < 4.2.
        # code above u can comment then.
        self.CLIENT_ID = imgur_access['CLIENT_ID']           <-- unhash those
        self.CLIENT_SECRET = imgur_access["CLIENT_SECRET"]
        self.CLIENT_USERNAME = imgur_access["CLIENT_USERNAME"]
        self.ACCESS_TOKEN = imgur_access["ACCESS_TOKEN"]
        self.REFRESH_TOKEN = imgur_access["REFRESH_TOKEN"]
        self.base_api_url = imgur_access['base_api_url']

Now set up your `settings.py`. Do it even you are using **Django <= 4.2**:

    STORAGES = {  
        "default": {  
            "BACKEND": "django.core.files.storage.FileSystemStorage",  
        },  
        "staticfiles": {  
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",  
        },  
      "imgur": {  
            "BACKEND": "czarny_kot.imgur_storage.ImgurStorage",  
            "OPTIONS": {  
                "base_api_url": "https://api.imgur.com/3/",  
                "location": "",  
                "CLIENT_ID": env("IMGUR_CONSUMER_ID"),  
                "CLIENT_SECRET": env("IMGUR_CONSUMER_SECRET"),  
                "CLIENT_USERNAME": env("IMGUR_USERNAME"),  
                "ACCESS_TOKEN": env("IMGUR_ACCESS_TOKEN"),  
                "REFRESH_TOKEN": env("IMGUR_ACCESS_TOKEN_REFRESH"),  
            }  
        },  
    }
You don't need change any `MEDIA_URL` or `MEDIA_ROOT` . You will able to use default storage as so far. 
It's high time to tell Django about the custom storage backend you’ll be using. Do it in your `models.py`file. If you are using **Django >= 4.2** you have to add below lines:

    from django.core.files.storage import storages
    
    STORAGE = storages['imgur']

If you are using older version of **Django < 4.2** you need to add such lines in your `models.py`:

    from czarny_kot.imgur_storage import ImgurStorage
        
    STORAGE = ImgurStorage()

Don't forget to add custom storage to yours models. You can do it using attribute `storage=` :

    class Post(models.Model):  
        # ...  
        photo_carousel_imgur = models.ImageField(  
		    upload_to='CzornyKotPL', storage=STORAGE, verbose_name='Niskie do karuzeli',  
		    null=True, blank=True, help_text='Proporcja: 1973x1110'  
		)  
		photo_feat_imgur = models.ImageField(  
		    upload_to='CzornyKotPL', storage=STORAGE, verbose_name='Do fita i kropki', 
		    null=True, blank=True, help_text='Proporcja: kwadrat'  
		)
        # ...
In your **template** you can lookup for the image in such way (add `referrerpolicy=` to avoid problems with displaying images):

    <img src="{{ post.2.photo_feat_imgur.url }}" referrerpolicy="no-referrer" alt={{ post.2.carousel_title }}>
And that's all. Everyfing should work perfectly. Easy, smothly, without problems :)
More about writing custom storages you can find here: [docs.djangoproject.com/en/4.2/howto/custom-file-storage/](https://docs.djangoproject.com/en/4.2/howto/custom-file-storage/)
