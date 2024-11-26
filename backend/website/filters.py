def filter_djoser_paths(endpoints):
    filtered = []
    for (path, path_regex, method, callback) in endpoints:
        if not path.startswith('/api/auth/users/'):
            filtered.append((path, path_regex, method, callback))
    return filtered
