import argparse
import json
import os
import requests
import shutil

from datetime import datetime
from urlparse import urlparse

import pytumblr

DEFAULT_PAGE_SIZE = 20


class TumblrBackup(object):
    def __init__(self, consumer_key, consumer_secret, blog_name,
                 export_destination):
        super(TumblrBackup, self).__init__()

        self.blog_name = blog_name
        self.export_destination = export_destination
        self.posts_processed = 0

        self.tumblr_client = pytumblr.TumblrRestClient(
            consumer_key, consumer_secret)

    def execute(self):
        print self.blog_name
        total_posts = self._get_total_posts()

        offset = 0
        pages, remainder = divmod(total_posts, DEFAULT_PAGE_SIZE)
        if pages == 0:
            pages += 1
        if remainder > 0:
            pages += 1

        for i in range(0, pages):
            params = {'offset': i * DEFAULT_PAGE_SIZE}
            posts = self.tumblr_client.posts(self.blog_name, **params)
            if 'meta' in posts and posts['meta']['status'] != 200:
                print 'Error getting posts: {}'.format(posts['meta']['msg'])
                continue

            for post in posts['posts']:
                post_directory_name = datetime.utcfromtimestamp(post['timestamp']).strftime('%Y_%m_%d_%H_%M_%S')
                output_dir = os.path.join(self.export_destination,
                                          post_directory_name)

                self._save_post(post, output_dir)

                if post['type'] == 'photo':
                    self._save_photos(post['photos'], output_dir)

        print('Saved {} posts out of {}'.format(self.posts_processed, total_posts))

    def _get_total_posts(self):
        blog_info = self.tumblr_client.blog_info(self.blog_name)
        if 'meta' in blog_info and blog_info['meta']['status'] != 200:
            print 'Error getting total posts: {}'.format(blog_info['meta']['msg'])
            return 0

        total_posts = blog_info['blog']['posts']
        print(total_posts)
        return total_posts

    def _save_post(self, post, output_dir):
        print('Saving post: {}'.format(post['id']))
        # create output directory for the post
        try:
            os.makedirs(output_dir)
        except OSError:
            pass

        post_type = post['type']
        filename = "{}_{}.json".format(post['id'], post_type)
        output_filepath = os.path.join(output_dir, filename)
        with open(output_filepath, 'w') as f:
            f.write(json.dumps(post, indent=2))

        self.posts_processed += 1

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
