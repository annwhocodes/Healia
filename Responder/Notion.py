from notion_client import Client
from config import NOTION_KEY, PAGE_ID
from datetime import datetime

class NotionDB:
    def __init__(self, database_title="New Database"):
        self.notion = Client(auth=NOTION_KEY)
        self.parent_page_id = PAGE_ID
        self.database_title = database_title
        self.database_id = self.get_or_create_database()
    def get_or_create_database(self):
        # Check if database already exists in the parent page
        children = self.notion.blocks.children.list(self.parent_page_id)['results']

        for child in children:
            if child['object'] == 'block' and child['type'] == 'child_database':
                if child['child_database']['title'] == self.database_title:
                    return child['id']

        # If not found, create a new database
        properties = {
            'Patient Name': {'title': {}},
            'Description': {'rich_text': {}},
            'Date': {'date': {}},
            'Time': {'rich_text': {}}  # Add a Files property for the image
        }

        database = self.notion.databases.create(
            parent={'type': 'page_id', 'page_id': self.parent_page_id},
            title=[{'type': 'text', 'text': {'content': self.database_title}}],
            properties=properties
        )
        return database['id']

    def add_entry(self, name, description, date, image_url=None):
        properties = {
            'Patient Name': {
                'title': [
                    {
                        'text': {
                            'content': name
                        }
                    }
                ]
            },
            'Description': {
                'rich_text': [
                    {
                        'text': {
                            'content': description
                        }
                    }
                ]
            },
            'Date': {
                'date': {
                    'start': date
                }
            },
            'Time': {
                'rich_text': [
                    {
                        'text': {
                            'content': datetime.now().strftime("%H:%M:%S")
                        }
                    }
                ]
            }
        }

        # Add image to properties if image_url is provided
        if image_url:
            properties['Image'] = {
                'files': [
                    {
                        'name': 'image.png',  # You can customize the image name
                        'external': {'url': image_url},
                    }
                ]
            }

        # Create the page
        new_page = self.notion.pages.create(
            parent={'database_id': self.database_id},
            properties=properties
        )

        # Add content to the body of the new page
        children_blocks = [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {
                                "content": description
                            }
                        }
                    ]
                }
            }
        ]

        # Add image block to the body if image_url is provided
        if image_url:
            children_blocks.append(
                {
                    "object": "block",
                    "type": "image",
                    "image": {
                        "type": "external",
                        "external": {
                            "url": image_url
                        }
                    }
                }
            )

        self.notion.blocks.children.append(
            block_id=new_page['id'],
            children=children_blocks
        )

if __name__ == "__main__":
    db = NotionDB(database_title="My Task Table with Image")
    sample_image_url = "https://www.easygifanimator.net/images/samples/video-to-gif-sample.gif"  # Replace with your image URL
    db.add_entry(
        name="Entry with Image",
        description="This entry has an image.",
        date=datetime.now().strftime("%Y-%m-%d"),
        image_url=sample_image_url
    )
    db.add_entry(
        name="Another Entry",
        description="This entry does not have an image.",
        date=datetime.now().strftime("%Y-%m-%d")
    )
