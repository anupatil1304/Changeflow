def get_developer_visible_request_ids(development_rows, current_user_id):
    visible_ids = []
    for row in development_rows:
        if row.AssignedTo in (None, current_user_id):
            visible_ids.append(row.RequestID)
    return visible_ids
