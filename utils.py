from reportlab.platypus import SimpleDocTemplate, Paragraph, Image, ParagraphAndImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib.units import cm
from StringIO import StringIO
from datetime import tzinfo, timedelta, datetime
from copy import deepcopy
import time


# the following code is used to make datetime.now() be TZ aware
# taken directly from the python docs: http://docs.python.org/2/library/datetime.html#tzinfo-objects
STDOFFSET = timedelta(seconds = -time.timezone)
if time.daylight:
    DSTOFFSET = timedelta(seconds = -time.altzone)
else:
    DSTOFFSET = STDOFFSET

DSTDIFF = DSTOFFSET - STDOFFSET

class LocalTimezone(tzinfo):

    def utcoffset(self, dt):
        if self._isdst(dt):
            return DSTOFFSET
        else:
            return STDOFFSET

    def dst(self, dt):
        if self._isdst(dt):
            return DSTDIFF
        else:
            return timedelta(0)

    def tzname(self, dt):
        return time.tzname[self._isdst(dt)]

    def _isdst(self, dt):
        tt = (dt.year, dt.month, dt.day,
              dt.hour, dt.minute, dt.second,
              dt.weekday(), 0, 0)
        stamp = time.mktime(tt)
        tt = time.localtime(stamp)
        return tt.tm_isdst > 0


def compose_pdf(profile):
    """Generates the pdf file based on the profile returned by the linkedin API."""
    output = StringIO()

    # some constants
    FONT_NAME = 'Helvetica'
    FONT_SIZE = 12
    COLOR = '#aaabbb'
    LEADING = 16
    HEADLINE_FONT_SIZE = 18
    PARAGRAPH_SPACE = 30
    BULLET_INDENT = 10
    #FIXME (Iurii Kudriavtsev): image should be scaled appropriately
    IMG_WIDTH = 3*cm
    IMG_HEIGHT = 4*cm

    doc = SimpleDocTemplate(
        output,
        # pagesize=letter,
        topMargin=2*cm,
        rightMargin=cm,
        bottomMargin=2*cm,
        leftMargin=cm,
    )

    # define styles that will be used
    styles=getSampleStyleSheet()
    styles["Normal"].fontName = FONT_NAME
    styles["Normal"].fontSize = FONT_SIZE
    styles["Normal"].leading = LEADING
    styles["Normal"].alignment = TA_JUSTIFY
    styles["Normal"].spaceBefore = 20
    styles["Normal"].spaceAfter = 10
    styles.add(ParagraphStyle(
        name='Headline',
        alignment=TA_CENTER,
        fontName=FONT_NAME,
        fontSize=HEADLINE_FONT_SIZE,
        leading = LEADING,
        spaceBefore=PARAGRAPH_SPACE,
        spaceAfter=PARAGRAPH_SPACE
        )
    )
    Indent_style = deepcopy(styles["Normal"])
    Indent_style.name = 'Indent'
    Indent_style.fontSize = 10
    Indent_style.leftIndent = 30
    Indent_style.spaceBefore = 0
    Indent_style.spaceAfter = 0
    Indent_style.bulletIndent = 20
    styles.add(Indent_style)
    Bullet_style = deepcopy(styles["Normal"])
    Bullet_style.name = 'CustomBullet'
    Bullet_style.bulletFontName = 'Symbol'
    Bullet_style.bulletFontSize = FONT_SIZE
    Bullet_style.firstLineIndent = 0
    Bullet_style.leftIndent = FONT_SIZE + BULLET_INDENT
    Bullet_style.bulletIndent = BULLET_INDENT
    Bullet_style.bulletColor = COLOR
    styles.add(Bullet_style)
    Skill_style = deepcopy(styles["Normal"])
    Skill_style.name = 'Skill'
    Skill_style.fontSize = 15
    Skill_style.fontName = 'Courier'
    Skill_style.textColor = COLOR
    styles.add(Skill_style)

    story = []
    p = '<font size=%d>%s %s</font><br/><br/>' % (HEADLINE_FONT_SIZE, profile['firstName'], profile['lastName'])
    p += '%s<br/><br/><br/>' % profile['headline']
    if profile['phoneNumbers']['_total']:
        p += '<strong>Phone:</strong>&nbsp;&nbsp;&nbsp;&nbsp;<font size=10>%s</font><br/><br/>' % profile['phoneNumbers']['values'][0]['phoneNumber']
    p += '<strong>Email:</strong>&nbsp;&nbsp;&nbsp;&nbsp;<font size=10>%s</font><br/><br/>' % profile['emailAddress']
    p += '<strong>Location:</strong>&nbsp;&nbsp;&nbsp;&nbsp;<font size=10>%s</font><br/><br/>' % profile['location']['name']
    p = Paragraph(p, styles["Normal"])
    if profile['pictureUrls']['_total']:
        profile_picture_url = profile['pictureUrls']['values'][0]
        img = Image(profile_picture_url, IMG_WIDTH, IMG_HEIGHT)
        story.append(ParagraphAndImage(p, img))
    story.append(Paragraph('Objective', styles["Headline"]))
    story.append(Paragraph(profile['summary'], styles["Normal"]))
    if profile['positions']['_total']:
        story.append(Paragraph('Work Experience', styles["Headline"]))
    for position in profile['positions']['values']:
        position_headline = '%s - %s <font color="%s">|</font> <font size=8>%d/%d - %s</font>' % (
            position['title'],
            position['company']['name'],
            COLOR,
            position['startDate']['month'],
            position['startDate']['year'],
            'present' if position['isCurrent'] else str(position['endDate']['month']) + '/' + str(position['endDate']['year']),
        )
        position_summary = position['summary'].replace('\n', '<br/>')
        story.append(Paragraph(position_headline, styles["CustomBullet"], bulletText='\xe2\x80\xa2'))
        story.append(Paragraph(position_summary, styles["Indent"]))
    if profile['educations']['_total']:
        story.append(Paragraph('Education', styles["Headline"]))
    for education in profile['educations']['values']:
        education_headline = '%s <font color="%s">|</font> <font size=8>%d - %d</font>' % (
            education['schoolName'],
            COLOR,
            education['startDate']['year'],
            education['endDate']['year'],
        )
        education_headline += '<br/>%s, %s' % (education['degree'], education['fieldOfStudy'])
        story.append(Paragraph(education_headline, styles["CustomBullet"], bulletText='\xe2\x80\xa2'))
        for note in education['notes'].split('\n'):
            story.append(Paragraph(note, styles["Indent"], bulletText='-'))
    if profile['skills']['_total']:
        story.append(Paragraph('Skills', styles["Headline"]))
    p = '  '.join([skill['skill']['name'].upper() for skill in profile['skills']['values']])
    story.append(Paragraph(p, styles["Skill"]))
    if profile['recommendationsReceived']['_total']:
        story.append(Paragraph('Recommendations', styles["Headline"]))
    for recommendation in profile['recommendationsReceived']['values']:
        recommendation_headline = '%s %s <font color="%s">|</font> <font size=8>%s</font>' % (
            recommendation['recommender']['firstName'],
            recommendation['recommender']['lastName'],
            COLOR,
            recommendation['recommendationType']['code'],
        )
        recommendation_text = recommendation['recommendationText'].replace('\n', '<br/>')
        story.append(Paragraph(recommendation_headline, styles["CustomBullet"], bulletText='\xe2\x80\xa2'))
        story.append(Paragraph(recommendation_text, styles["Indent"]))

    def onPage(canvas, dcmt):
        canvas.saveState()
        canvas.setFont(FONT_NAME, 7)
        canvas.setStrokeColor(COLOR)
        canvas.setFillColor(COLOR)
        canvas.drawString(cm, dcmt.pagesize[1] - .75*cm,
            '%s %s - %s' % (profile['firstName'], profile['lastName'], profile['headline']))
        Local = LocalTimezone()
        canvas.drawRightString(dcmt.pagesize[0] - cm, dcmt.pagesize[1] - .75*cm,
            datetime.now(Local).strftime('Generated on %d.%m.%Y %H:%M:%S %Z'))
        canvas.line(cm, dcmt.pagesize[1] - cm, dcmt.pagesize[0] - cm, dcmt.pagesize[1] - cm)
        canvas.line(cm, cm, (dcmt.pagesize[0] - cm)/2.0, cm)
        canvas.drawCentredString(dcmt.pagesize[0]/2.0, .95*cm, str(dcmt.page))
        canvas.line((dcmt.pagesize[0] + cm)/2.0, cm, dcmt.pagesize[0] - cm, cm)
        canvas.restoreState()

    doc.build(story, onFirstPage=onPage, onLaterPages=onPage)

    pdf = output.getvalue()
    output.close()
    return pdf
