import argparse
import json

import pytumblr


class TumblrBackup(object):
    def __init__(self, consumer_key, consumer_secret, blog_name, export_destination):
        super().__init__()

        self.blog_name = blog_name
        self.export_destination = export_destination

        self.tumblr_client = pytumblr.TumblrRestClient(
            consumer_key, consumer_secret)

    def execute(self):
        posts = self.tumblr_client.posts(self.blog_name)
        print(posts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('consumer_key', metavar='consumer_key', type=str,
                        help='Tumblr API consumer key')
    parser.add_argument('consumer_secret', metavar='consumer_secret',
                        type=str, help='Tumblr API consumer secret')
    parser.add_argument('blog_name', metavar='blog_name', type=str,
                        help='Tumblr blog name')
    parser.add_argument('export_destination', metavar='export_destination', type=str,
                        help='Directory for export files')

    args = parser.parse_args()

    backup = TumblrBackup(**vars(args))
    backup.execute()
