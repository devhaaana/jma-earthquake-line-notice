import re


# 위도 경도 진앙깊이 나누기
def parse_coordinates(coord_string):
    match = re.match(r'([+|-]\d{2}.\d+)([+|-]\d{3}.\d+)(.*)/', coord_string)
    
    return tuple(map(float, match.groups()))


def parse_coordinates_DEI(coord_string):
    match = re.match(r'([+|-]\d{2}.\d+)([+|-]\d{3}.\d+)', coord_string)
    
    return tuple(map(float, match.groups()))