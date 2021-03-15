from sqlalchemy import create_engine, String, Column, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from tkinter import *
from tkinter import ttk
from ttkwidgets import Table

from sqlalchemy.sql.elements import ColumnClause

SUBJECTS = ['Maths', 'Physique-Chimie', 'Anglais', 'EPS', 'Enseignement Scientifique', 'Espagnol', 'Histoire-Géo', 'Philosophie', 'Français', 'LLCE', 'Bulletins 1ère']
COEFS = [16, 16, 5, 5, 5, 5, 5, 8, 10, 5, 10]
TRIMESTERS = ['Trimestre 1', 'Trimestre 2', 'Trimestre 3']

engine = create_engine('sqlite:///graduations.db')
db = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class AddGraduation(db):
    __tablename__ = "Graduations"
    id = Column(Integer, primary_key=True)
    trimester = Column(String)
    subject = Column(String)
    graduation = Column(Float)
    coef = Column(Float)

class GlobalAveragesBySubject(db):
    __tablename__ = "GlobalAveragesBySubject"
    id = Column(Integer, primary_key=True)
    subject = Column(String)
    average = Column(Float)

class AveragesBySubjectByTrimesters(db):
    __tablename__ = "AveragesBySubjectByTrimesters"
    id = Column(Integer, primary_key=True)
    subject = Column(String)
    average = Column(Float)
    trimester = Column(String)

class AveragesByTrimester(db):
    __tablename__ = "AveragesByTrimester"
    id = Column(Integer, primary_key=True)
    average = Column(Float)
    trimester = Column(String)


db.metadata.create_all(engine)

def calculate_avg_trimester_by_subject():
    for t in TRIMESTERS:
        for s in SUBJECTS:
            all_grad = session.query(AddGraduation).filter_by(subject=s, trimester=t).all()
            if all_grad != []:
                average = round(sum([g.graduation*g.coef for g in all_grad]) / sum([g.coef for g in all_grad]), 2)
                try:
                    subject_avg = session.query(AveragesBySubjectByTrimesters).filter_by(subject=s, trimester=t).first()
                    subject_avg.average = average
                    session.commit()
                except:
                    new_avg = AveragesBySubjectByTrimesters(
                        subject=s,
                        trimester=t,
                        average=average
                    )
                    session.add(new_avg)
                    session.commit()

def calculate_avg_global_by_subject():
    for s in SUBJECTS:
        try:
            subject_grads = session.query(AddGraduation).filter_by(subject=s).all()
            #Calculate Avg By Subject
            if subject_grads != []:
                subject_avg = round(sum([g.graduation*g.coef for g in subject_grads]) / sum([g.coef for g in subject_grads]), 2)
                try:
                    select_subject = session.query(GlobalAveragesBySubject).filter_by(subject=s).first()
                    select_subject.average = subject_avg
                    session.commit()
                except:
                    new_g_subject_avg = GlobalAveragesBySubject(
                        subject=s,
                        average=subject_avg
                    )
                    session.add(new_g_subject_avg)
                    session.commit()
        except:
            pass

def calculate_avg_trimester():
    for t in TRIMESTERS:
        try:
            all_subjects_avg = session.query(AveragesBySubjectByTrimesters).filter_by(trimester=t).all()
            if all_subjects_avg != []:
                avg_trimester = round(sum([s.average for s in all_subjects_avg]) / len(all_subjects_avg), 2)
                try:
                    select_t = session.query(AveragesByTrimester).filter_by(trimester=t).first()
                    select_t.average = avg_trimester
                    session.commit()
                except:
                    new_t_avg = AveragesByTrimester(
                        trimester=t,
                        average=avg_trimester
                    )
                    session.add(new_t_avg)
                    session.commit()

        except:
            pass

def calculate_proj_bac():
    #Get all global averages
    all_global_avg = session.query(GlobalAveragesBySubject).all()
    if len(all_global_avg) == len(SUBJECTS):
        all_global_avg_sorted = [session.query(GlobalAveragesBySubject).filter_by(subject=SUBJECTS[i]).first() for i in range(len(SUBJECTS))]
        avgs_with_coefs = [all_global_avg_sorted[j].average*COEFS[j] for j in range(len(SUBJECTS))]
        proj_bac = round(sum(avgs_with_coefs)/sum(COEFS), 2)
        return proj_bac
    else:
        return False

def add_graduation():
    try:
        trimester = trimester_choice.get()
        subject = subject_choice.get()
        coef = float(coef_entry.get())
        grad = float(graduation_entry.get())
        max = float(graduation_entry_max.get())

    except:
        return

    if trimester in TRIMESTERS and subject in SUBJECTS:
        #Convert graduation
        grad /= (max/20)
        coef *= (max/20)
        new_grade = AddGraduation(
            trimester = trimester,
            subject = subject,
            graduation = grad,
            coef = coef,
        )
        session.add(new_grade)
        session.commit()

def clear_entry():
    subject_choice.delete(0, END)
    trimester_choice.delete(0, END)
    graduation_entry.delete(0, END)
    graduation_entry_max.delete(0, END)
    coef_entry.delete(0, END)

def update_table():
    add_graduation()
    calculate_avg_trimester_by_subject()
    calculate_avg_global_by_subject()
    calculate_avg_trimester()
    calculate_proj_bac()
    clear_entry()


    r=1
    c=4
    for s in SUBJECTS:
        all_tr_avg = []
        for t in TRIMESTERS:
            avg_by_tr = session.query(AveragesBySubjectByTrimesters).filter_by(subject=s, trimester=t).first()
            if avg_by_tr != None:
                all_tr_avg.append(avg_by_tr.average)
            elif avg_by_tr == None:
                all_tr_avg.append("N.Not")

        new_r = TableRow()
        new_r.subject=s

        if len(all_tr_avg) >= 1:
            new_r.avg_t1 = all_tr_avg[0]
        if len(all_tr_avg) >= 2:
            new_r.avg_t2 = all_tr_avg[1]
        if len(all_tr_avg) >= 3:
            new_r.avg_t3 = all_tr_avg[2]

        global_avg = session.query(GlobalAveragesBySubject).filter_by(subject=s).first()
        if global_avg != None:
            new_r.avg_global = global_avg.average

        s_label = ttk.Label(text=new_r.subject, font="Arial 10 bold")
        s_label.config(padding=5)
        s_label.grid(row=r, column=c)

        t1_label = ttk.Label(text=new_r.avg_t1)
        t1_label.config(padding=5)
        t1_label.grid(row=r, column=c+1)

        t2_label = ttk.Label(text=new_r.avg_t2)
        t2_label.config(padding=5)
        t2_label.grid(row=r, column=c+2)

        t3_label = ttk.Label(text=new_r.avg_t3)
        t3_label.config(padding=5)
        t3_label.grid(row=r, column=c+3)

        avg_label = ttk.Label(text=new_r.avg_global)
        avg_label.config(padding=5)
        avg_label.grid(row=r, column=c+4)

        r+=1

    proj_bac = calculate_proj_bac()
    if proj_bac != False:
        proj_bac_label = ttk.Label(text="Proj. Bac", font="Arial 10 bold")
        proj_bac_label.config(padding=5)
        proj_bac_label.grid(row=r, column=c)

        proj_bac_avg_label = ttk.Label(text=proj_bac)
        proj_bac_avg_label.config(padding=5)
        proj_bac_avg_label.grid(row=r, column=c+1)



class TableRow():
    def __init__(self):
        self.subject = ""
        self.avg_t1 = "N.Not"
        self.avg_t2 = "N.Not"
        self.avg_t3 = "N.Not"
        self.avg_global = "N.Not"


root = Tk(screenName="Automate Grade Calculator")
root.config(padx=100, pady=50)
root.title('Automate Grade Calculator')

#Title
title_label = ttk.Label(text="Automate Grade Calculator")
title_label.grid(column=1, row=0, columnspan=3)

#Select Subject
subject_label = ttk.Label(text="Subject : ")
subject_label.grid(column=0, row=1)

subject_choice = ttk.Combobox(values=SUBJECTS)
subject_choice.grid(column=1, row=1, columnspan=3)

#Select Trimester
trimester_label = ttk.Label(text="Trimester : ")
trimester_label.config(padding=10)
trimester_label.grid(column=0, row=2)

trimester_choice = ttk.Combobox(values=TRIMESTERS)
trimester_choice.grid(column=1, row=2, columnspan=3)

#Input Graduate
graduation_label = ttk.Label(text="Graduation : ")
graduation_label.grid(column=0, row=3)

graduation_entry = ttk.Entry(width=8)
graduation_entry.grid(column=1, row=3, columnspan=1)

graduation_slash = ttk.Label(text="/")
graduation_slash.grid(column=2, row=3)

graduation_entry_max = ttk.Entry(width=8)
graduation_entry_max.grid(column=3, row=3, columnspan=1)

#Input Coef
coef_label = ttk.Label(text="Coeffiecient : ")
coef_label.config(padding=10)
coef_label.grid(column=0, row=4)

coef_entry = ttk.Entry(width=8)
coef_entry.grid(column=1, row=4)

#Buttons
add_graduation_button = ttk.Button(text="Add Graduation", command=update_table)
add_graduation_button.config(padding=5)
add_graduation_button.grid(column=1, row=5, columnspan=3)

#Table
#Create 1st Row
t1_label = ttk.Label(text="Trimester 1", font="Arial 10 bold")
t1_label.config(padding=2)
t1_label.grid(column=5, row=0)

t1_label = ttk.Label(text="Trimester 2", font="Arial 10 bold")
t1_label.config(padding=2)
t1_label.grid(column=6, row=0)

t1_label = ttk.Label(text="Trimester 3", font="Arial 10 bold")
t1_label.config(padding=2)
t1_label.grid(column=7, row=0)

t1_label = ttk.Label(text="Global", font="Arial 10 bold")
t1_label.config(padding=2)
t1_label.grid(column=8, row=0)

#Create Rows


update_table()







root.mainloop()
