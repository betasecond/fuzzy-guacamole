import json
import os

# URL prefix
url_prefix = "https://www.yuque.com/chengxuyuancarl/cnopdt/"

# Read the JSON file
with open('list.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create a mapping from uuid to title for parent lookups
uuid_to_item = {item['uuid']: item for item in data['data']}

# Process each item in the data list
for item in data['data']:
    if item['type'] == 'DOC' and item['url']:
        
        path_parts = []
        current_item = item
        while current_item and current_item.get('parent_uuid'):
            parent_uuid = current_item.get('parent_uuid')
            parent_item = uuid_to_item.get(parent_uuid)
            if parent_item:
                # Sanitize and prepend parent title to path
                parent_title = parent_item['title'].strip().replace('/', '_').replace(':', '_')
                path_parts.insert(0, parent_title)
                current_item = parent_item
            else:
                # No more parents
                current_item = None
        
        # Add current item's title
        title = item['title'].strip().replace('/', '_').replace(':', '_')
        path_parts.append(title)

        folder_path = os.path.join(*path_parts)

        if not folder_path:
            continue

        # Create directory if it doesn't exist
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Create README.md file
        readme_path = os.path.join(folder_path, 'README.md')
        with open(readme_path, 'w', encoding='utf-8') as readme_file:
            full_url = url_prefix + item['url']
            readme_file.write(f"# {item['title']}\n\n")
            readme_file.write(f"URL: {full_url}\n")

        print(f"Created folder: {folder_path}")

print("Script finished.")
