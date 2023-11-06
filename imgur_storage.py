import base64
import requests
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class ImgurStorage(Storage):
    #
    def __init__(self, **kwargs):

        self.CLIENT_ID = kwargs.get("CLIENT_ID")
        self.CLIENT_SECRET = kwargs.get("CLIENT_SECRET")
        self.CLIENT_USERNAME = kwargs.get("CLIENT_USERNAME")
        self.ACCESS_TOKEN = kwargs.get("ACCESS_TOKEN")
        self.REFRESH_TOKEN = kwargs.get("REFRESH_TOKEN")
        self.base_api_url = kwargs.get('base_api_url')

        # configurations for hitting API
        self.requests_configs = {
            'get_albums': {
                'method': 'GET',
                'end_api_url': f"account/{self.CLIENT_USERNAME}/albums"
            },
            'create_album': {
                'method': 'POST',
                'end_api_url': 'album'
            },
            'get_image': {
                'method': 'GET',
                'end_api_url': 'image/'
            },
            'upload_image': {
                'method': 'POST',
                'end_api_url': 'image'
            },
            'delete_image': {
                'method': 'DELETE',
                'end_api_url': 'image/'
            }
        }

    # don't need this but must be not to save images in default media
    # directory. more: https://docs.djangoproject.com/en/4.2/howto/custom-file-storage/
    def _open(self, name, mode='rb'):
        pass

    def _save(self, name, content):
        # extract from name only part  'upload_to=' from ImageField in models.
        album_name = name.split('/')[0]
        albums = self.make_request('get_albums')

        # if response status code != 200 break (so were errors with API) method
        # and return name = 'brak' (no photo in polish). _save method must return string,
        # I don't want to save my post only because of problems with API.
        if not self.check_response(albums):
            return 'brak'

        album = [album for album in albums.json()['data'] if album['title'] == album_name]

        # create post on imgur or grab id of existing album
        if not album:
            __payload = {
                'title': album_name,
                'description': 'Fotki i obrazki z www'
            }

            album = self.make_request('create_album', payload=__payload)
            if not self.check_response(album):
                return 'brak'
            __album_id = album.json()['data']['id']
        else:
            __album_id = album[0]['id']

        # prepare content for uploading -
        __content = content.read()

        __payload = {
            # change files to accepted imgur format
            'image': base64.b64encode(__content),
            'album': __album_id,
            'title': name.split('/')[-1],
            'type': 'base64',
        }

        __image = self.make_request('upload_image', payload=__payload)
        if not self.check_response(albums):
            return 'brak'

        # name is going to be full link of uploaded image and this will be saved in database
        if __image:
            name = __image.json()['data']['link']
        else:
            return 'brak'
        return name

    # help method to make requests
    def make_request(self, request_config, auth=True, **kwargs):
        # grab all options given as arguments
        __config = self.requests_configs[request_config]
        __payload = kwargs.get('payload')
        __files = kwargs.get('files')
        __id = kwargs.get('element_id')

        if not __id:
            __id = ''

        if auth:
            __headers = {'Authorization': 'Bearer ' + self.ACCESS_TOKEN}

        else:
            __headers = {'Authorization': 'Client-ID ' + self.CLIENT_ID}

        return requests.request(
            __config['method'], self.base_api_url + __config['end_api_url'] + __id,
            headers=__headers, data=__payload, files=__files
        )

    @staticmethod
    def check_response(response):
        value = True if response.status_code == 200 else False
        return value

    def url(self, name):
        """
        Return an absolute URL where the file's contents can be accessed
        directly by a web browser.
        """
        return name

    def delete(self, name):
        # there is possibility of such string in db (brak means no photo).
        # in not such delete image on imgur
        if name != 'brak':
            # from string: https://i.imgur.com/03R0JBY.png' I need only last part without .png
            __image_id = name.split('/')[-1].split('.')[0]
        else:
            __image_id = ''
        return self.make_request('delete_image', element_id=__image_id)

    def img_exists(self, name):

        __image_id = name.split('/')[-1].split('.')[0]
        response = self.make_request('get_image', element_id=__image_id)

        # return False if there is the image on imgur not to stop uploading image
        return self.check_response(response)

    # don't need stuff below but must be not to have NotImplementedError:
    # https://docs.djangoproject.com/en/4.2/howto/custom-file-storage/
    def listdir(self, path):
        """
        List the contents of the specified path. Return a 2-tuple of lists:
        the first item being directories, the second item being files.
        """
        pass

    def size(self, name):
        """
        Return the total size, in bytes, of the file specified by name.
        """
        pass

    def exists(self, name):
        """
        Return True if a file referenced by the given name already exists in the
        storage system, or False if the name is available for a new file.
        """
        pass

    def get_accessed_time(self, name):
        """
        Return the last accessed time (as a datetime) of the file specified by
        name. The datetime will be timezone-aware if USE_TZ=True.
        """
        pass

    def get_created_time(self, name):
        """
        Return the creation time (as a datetime) of the file specified by name.
        The datetime will be timezone-aware if USE_TZ=True.
        """
        pass

    def get_modified_time(self, name):
        """
        Return the last modified time (as a datetime) of the file specified by
        name. The datetime will be timezone-aware if USE_TZ=True.
        """
        pass
