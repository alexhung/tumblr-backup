import argparse
import json
import os
import requests
import shutil

from datetime import datetime
from urllib.parse import urlparse

import pytumblr


class TumblrBackup(object):
    def __init__(self, consumer_key, consumer_secret, blog_name,
                 export_destination):
        super().__init__()

        self.blog_name = blog_name
        self.export_destination = export_destination

        self.tumblr_client = pytumblr.TumblrRestClient(
            consumer_key, consumer_secret)

    def execute(self):
        posts = self.tumblr_client.posts(self.blog_name)
        for post in posts['posts']:
            print('Saving post: {}'.format(post['id']))
            # create output directory for the post
            post_directory_name = datetime.utcfromtimestamp(post['timestamp']).strftime('%Y_%m_%d_%H_%M_%S')
            output_dir = os.path.join(self.export_destination,
                                      post_directory_name)
            os.makedirs(output_dir, exist_ok=True)

            post_type = post['type']
            filename = "{}_{}.json".format(post['id'], post_type)
            output_filepath = os.path.join(output_dir, filename)
            with open(output_filepath, 'w') as f:
                f.write(json.dumps(post, indent=2))

            if post_type == 'photo':
                self._save_photos(post['photos'], output_dir)

    def _save_photos(self, post_photos, output_dir):
        for photo in post_photos:
            original_photo_url = photo['original_size']['url']

            url_obj = urlparse(original_photo_url)
            photo_filepath = os.path.join(output_dir, os.path.basename(url_obj.path))

            print('Saving photo: {}'.format(photo_filepath))
            try:
                response = requests.get(original_photo_url, stream=True)
            except requests.exceptions.RequestException:
                print('Failed to download photo: {}'.format(original_photo_url))
            else:
                with open(photo_filepath, 'wb') as f:
                    shutil.copyfileobj(response.raw, f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('consumer_key', metavar='consumer_key', type=str,
                        help='Tumblr API consumer key')
    parser.add_argument('consumer_secret', metavar='consumer_secret',
                        type=str, help='Tumblr API consumer secret')
    parser.add_argument('blog_name', metavar='blog_name', type=str,
                        help='Tumblr blog name')
    parser.add_argument('export_destination', metavar='export_destination',
                        type=str, help='Directory for export files')

    args = parser.parse_args()

    backup = TumblrBackup(**vars(args))
    backup.execute()
