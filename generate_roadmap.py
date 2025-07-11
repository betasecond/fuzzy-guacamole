import json
import os
import re
import urllib.parse

def sanitize_title(title):
    """Sanitizes a title to be used as a valid directory name."""
    return title.strip().replace('/', '_').replace(':', '_')

def get_item_path(item, uuid_to_item):
    """Constructs the file path for a given item based on its parents."""
    path_parts = []
    current_item = item
    while current_item and current_item.get('parent_uuid'):
        parent_uuid = current_item.get('parent_uuid')
        parent_item = uuid_to_item.get(parent_uuid)
        if parent_item:
            path_parts.insert(0, sanitize_title(parent_item['title']))
            current_item = parent_item
        else:
            current_item = None
    
    path_parts.append(sanitize_title(item['title']))
    return os.path.join(*path_parts)

# Read the JSON file
try:
    with open('list.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error: list.json not found.")
    exit()
except json.JSONDecodeError:
    print("Error: Could not decode list.json.")
    exit()

# Create a mapping from uuid to item for efficient lookups
all_items = data.get('data', [])
uuid_to_item = {item['uuid']: item for item in all_items}

# Filter for only the document items that have a URL
doc_items = [item for item in all_items if item.get('type') == 'DOC' and item.get('url')]

# Separate items into daily plan and other topics
daily_plan_items = []
other_topics_items = []

for item in doc_items:
    title = item.get('title', 'Unnamed Task')
    # Use regex to find titles that match the "chapter/part" format
    if re.search(r'第.*章.*part', title, re.IGNORECASE):
        daily_plan_items.append(item)
    else:
        other_topics_items.append(item)

# Start generating the markdown content
markdown_content = "# LeetCode / Algorithm Roadmap\n\n"
markdown_content += "A day-by-day plan to tackle the algorithm challenges.\n\n"

# Generate the daily roadmap
markdown_content += "## Daily Plan\n\n"
day_counter = 1
for item in daily_plan_items:
    title = item.get('title', 'Unnamed Task')
    folder_path = get_item_path(item, uuid_to_item)
    if not folder_path:
        continue
    readme_path = os.path.join(folder_path, 'README.md').replace('\\', '/')
    readme_link = urllib.parse.quote(readme_path, safe='/')
    markdown_content += f"- Day {day_counter}: [{title}]({readme_link})\n"
    day_counter += 1

# Generate the other topics section
markdown_content += "\n## Other Topics\n\n"
for item in other_topics_items:
    title = item.get('title', 'Unnamed Task')
    folder_path = get_item_path(item, uuid_to_item)
    if not folder_path:
        continue
    readme_path = os.path.join(folder_path, 'README.md').replace('\\', '/')
    readme_link = urllib.parse.quote(readme_path, safe='/')
    markdown_content += f"- [{title}]({readme_link})\n"


# Write the generated content to the main README.md file
try:
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)
    print("Successfully generated roadmap and updated README.md.")
except IOError as e:
    print(f"Error writing to README.md: {e}")