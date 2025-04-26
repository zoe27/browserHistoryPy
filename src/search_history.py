import json

def search_history(query, history_items):
    """
    根据查询条件搜索历史记录
    """
    filtered_result = [
        item for item in history_items
        if query.lower() in item['title'].lower() or query.lower() in item['url'].lower()
    ]
    return filtered_result