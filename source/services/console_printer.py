def dashed_printer(text):
    text_length = len(text) + 6
    dashes = ''.join(['-' for _ in range(text_length)])
    print(dashes)
    print('|  ' + text + '  |')
    print(dashes)

def star_enclosed_print(text):
    text_length = len(text) + 12
    stars = ''.join(['*' for _ in range(text_length)])
    print(stars)
    print('****  ' + text + '  ****')
    print(stars)
