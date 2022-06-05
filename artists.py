#!/usr/bin/env python3


class Artists:
    """Η κλάση καλλιτέχνης"""

    def __init__(
        self,
        constituentid,
        displayname="",
        artistbio="",
        nationality="",
        gender="",
        begindate="",
        enddate="",
        wikiqid="",
        ulan="",
    ):
        self.constituentid = constituentid
        self.displayname = displayname
        self.artistbio = artistbio
        self.nationality = nationality
        self.gender = gender
        self.begindate = begindate
        self.enddate = enddate
        self.wikiqid = wikiqid
        self.ulan = ulan

    def __str__(self):
        return f"\n{self.constituentid}\n{self.displayname}\n{self.artistbio}\n{self.nationality}\n{self.gender}\n{self.begindate}\n{self.enddate}\n{self.wikiqid}\n{self.ulan}\n"
