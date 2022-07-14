from django.utils.safestring import mark_safe


def essay_content(essay):
    clean_text = essay[2:-2]
    clean_text = clean_text.replace("\\n", "<br>")
    clean_text = clean_text.replace("\\r", "<br>")
    clean_text = mark_safe(clean_text)
    return clean_text


def convert_score(score):
    if score==0:
        band = "Low Band (Band 5 - 6)"
    elif score==1:
        band = "Moderate Band (Band 6.5 - 7.5)"
    else:
        band = "High Band (Band 8+)"
    return band