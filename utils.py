def calculate_bmi(weight, height_cm):
    if height_cm <= 0:
        return 0
    height_m = height_cm / 100
    return round(weight / (height_m ** 2), 2)


def age_risk(age_group):
    return {"<30": 0.5, "30-40": 1, "41-50": 2, ">50": 3}.get(age_group, 0)


def bmi_risk(bmi):
    if bmi < 18.5:
        return 0.5
    elif bmi < 25:
        return 1
    elif bmi < 30:
        return 2
    else:
        return 3


def genetic_risk(family_bc, ovarian_bc):
    score = 0
    if family_bc == "Yes":
        score += 3
    elif family_bc == "Don't Know":
        score += 1

    if ovarian_bc == "Yes":
        score += 2
    return score


def hormonal_risk(pills, menopause_meds):
    score = 0
    if pills == "Long time":
        score += 2
    elif pills == "Short time":
        score += 1

    if menopause_meds == "Long time":
        score += 2
    elif menopause_meds == "Short time":
        score += 1
    return score


def radiation_risk(xray):
    return {"Many times": 2, "Few times": 1, "Never": 0, "Don't Know": 0.5}.get(xray, 0)


def symptom_risk(lump, pain, discharge):
    score = 0
    if lump == "Yes":
        score += 3
    if pain == "Yes":
        score += 1
    if discharge == "Yes":
        score += 2
    return score


def reproductive_risk(early_period, late_menopause, late_pregnancy):
    score = 0
    if early_period == "Yes":
        score += 1.5
    if late_menopause == "Yes":
        score += 1.5
    if late_pregnancy == "Yes":
        score += 1.5
    return score


def lifestyle_risk(lifestyle):
    return 2 if lifestyle == "Yes" else 0.5
