import requests

# FIXME not simple to implement
# https://gist.github.com/alechemy/ed84c5b6b53b5194f1875b96a9a4faf1

# FFTA Mechanics Guide
FAQ_URL = (
    "https://gamefaqs.gamespot.com/gba/560436-final-fantasy-tactics-advance/faqs/26262"
)
GAME_FAQS_PARAMS = {"single": 1, "print": 1}  # get plain text download


def download_faq_text():
    response = requests.get(FAQ_URL, params=GAME_FAQS_PARAMS)
    if response.status_code == 200:
        with open("data/ffta-character-growths.txt", "w") as file:
            file.write(response.text)
    else:
        raise RuntimeError(
            f"Failed to download file "
            f"(code {response.status_code}) body: {response.text}"
        )

    return response.text
