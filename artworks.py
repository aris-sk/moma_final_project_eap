#!/usr/bin/env python3


class Artworks:
    """Η κλάση έργο τέχνης"""

    def __init__(
        self,
        title="",
        department="",
        artist="",
        nationality="",
        gender="",
        begindate="",
        enddate="",
        dimensions="",
        date="",
        dateacquired="",
        medium="",
        url="",
        thumbnailurl="",
        creditline="",
        objectid="",
        constituentid="",
    ):
        self.title = title
        self.department = department
        self.artist = artist
        self.nationality = nationality.strip("(").strip(")")
        self.gender = gender.strip("(").strip(")")
        self.begindate = begindate.strip("(").strip(")")
        self.enddate = enddate.strip("(").strip(")")
        self.dimensions = dimensions
        self.date = date
        self.dateacquired = "-".join(dateacquired.split("-")[::-1]) if dateacquired else ""
        self.medium = medium
        self.url = url
        self.thumbnailurl = thumbnailurl
        self.creditline = creditline
        self.objectid = objectid
        self.constituentid = constituentid

    def __str__(self):
        return f"\n{self.title}\n{self.department}\n{self.artist}\n{self.nationality}\n{self.gender}\n{self.begindate}\n{self.enddate}\n{self.dimensions}\n{self.date}\n{self.dateacquired}\n{self.medium}\n{self.url}\n{self.thumbnailurl}\n"
