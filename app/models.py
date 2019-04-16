from app import db

association_table = db.Table('association', db.Model.metadata,
    db.Column('tester_id', db.Integer, db.ForeignKey('tester.id')),
    db.Column('device_id', db.Integer, db.ForeignKey('device.id'))
)

class Bug(db.Model):
    # __tablename__ = 'bug'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    tester_id = db.Column(db.Integer, db.ForeignKey('tester.id'))

    def __repr__(self):
        return '<Bug {} found on {} by {}>'.format(self.id, self.device_id, self.tester_id)

class Device(db.Model):
    __tablename__ = 'device'
    id = db.Column(db.Integer, primary_key=True)
    device_name = db.Column(db.String(64), index=True, unique=True)
    testers = db.relationship("Tester", secondary=association_table, back_populates="devices")

    def __repr__(self):
        return '<{}>'.format(self.device_name)

class Experience(db.Model):
    # __tablename__ = 'experience'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'))
    bugs = db.Column(db.Integer)
    tester_id = db.Column(db.Integer, db.ForeignKey('tester.id'))

    def __repr__(self):
        return '<Tester {} has filed {} bugs on {}>'.format(self.tester_id, self.bugs, self.device_id)

class Tester(db.Model):
    # __tablename__ = 'tester'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), index=True)
    last_name = db.Column(db.String(64), index=True)
    country = db.Column(db.String(2), index=True)
    last_login = db.Column(db.DateTime, index=True)
    experience = db.relationship("Experience", backref="tester")
    devices = db.relationship("Device", secondary=association_table, back_populates="testers")

    def __repr__(self):
        return '<Tester {} {} from {} last seen {}>'.format(self.first_name, self.last_name, self.country, self.last_login)
    
    def name(self):
        return self.first_name + " " + self.last_name + " (" + self.country + ")"
