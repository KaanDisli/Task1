def check_params_add(body):
    l = ['firstname','lastname','password','gender']
    for elem in l: 
        if elem not in body:
            return False
    return True