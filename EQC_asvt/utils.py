import numpy as np
import face_recognition as fr
from qsystem.models import Profile

def is_ajax(request):
    return request.headers.get('x-requested-with') == 'XMLHttpRequest'

def get_encoded_faces():
    qs = Profile.objects.all()
    
    encoded = {}
    try:
        for p in qs:
            encoding = None
        
            face = fr.load_image_file(p.photo.path)
            print(p.photo.path)
            face_encodings = fr.face_encodings(face)
            if len(face_encodings) > 0:
                encoding = face_encodings[0]
            else:
                print("No face found in the image")

        # Add the user's encoded face to the dictionary if encoding is not None
            if encoding is not None:
                encoded[p.user.username] = encoding
    except:
        print("problem")

    # Return the dictionary of encoded faces
    return encoded


def classify_face(img):
    """
    This function takes an image as input and returns the name of the face it contains
    """
    # Load all the known faces and their encodings
    faces = get_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

    # Load the input image
    img = fr.load_image_file(img)
 
    try:
        # Find the locations of all faces in the input image
        face_locations = fr.face_locations(img)

        # Encode the faces in the input image
        unknown_face_encodings = fr.face_encodings(img, face_locations)

        # Identify the faces in the input image
        face_names = []
        for face_encoding in unknown_face_encodings:
            # Compare the encoding of the current face to the encodings of all known faces
            matches = fr.compare_faces(faces_encoded, face_encoding)

            # Find the known face with the closest encoding to the current face
            face_distances = fr.face_distance(faces_encoded, face_encoding)
            best_match_index = np.argmin(face_distances)

            # If the closest known face is a match for the current face, label the face with the known name
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            else:
                name = "Unknown"

            face_names.append(name)

        # Return the name of the first face in the input image
        return face_names[0]
    except:
        # If no faces are found in the input image or an error occurs, return False
        return False
    
rus_to_eng = {
    'а' : 'a', 
    'б' : 'b',
    'в' : 'v',
    'г' : 'g',
    'д' : 'd',
    'е' : 'e',
    'ё' : 'io',
    'ж' : 'zh',
    'з' : 'z',
    'и' : 'i',
    'й' : 'ii',
    'к' : 'k',
    'л' : 'l',
    'м' : 'm',
    'н' : 'n',
    'о' : 'o',
    'п' : 'p',
    'р' : 'r',
    'с' : 's',
    'т' : 't',
    'у' : 'u',
    'ф' : 'f',
    'х' : 'h',
    'ш' : 'sh',
    'щ' : 'sh',
    'ц' : 'c',
    'э' : 'e',
    'ю' : 'y',
    'я' : 'ia',
    'ы' : '',
    'ь' : '',
    'ъ' : ''
}

def bio_to_username(name : str, surname : str, group : str):
    username = ''
    if len(name) > 0:
        username += rus_to_eng[name[0]]
    if len(surname) > 0:
        username += rus_to_eng[surname[0]]
    username += '_'
    for l in group:
        if l in rus_to_eng:
            username += rus_to_eng[l]
        else:
            username += l
    return username
    