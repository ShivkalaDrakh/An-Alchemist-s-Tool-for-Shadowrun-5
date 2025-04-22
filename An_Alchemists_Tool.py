import random
import os
import subprocess
import json
import tkinter as tk
import ttkbootstrap as ttk
from tkinter.filedialog import asksaveasfilename, askopenfilename


Version = "V0.1"

# script dir will be used as initial for load/save
script_dir=os.path.dirname(os.path.realpath(__file__))
init_dir =os.path.join(script_dir,'init')
save_dir = os.path.join(init_dir,'save')
pdf_dir =  os.path.join(script_dir,r"..\Shadowrun [multi]\5th Edition")
path_to_acrobat = os.path.abspath(r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe")

#TODOs:
# - add reagents
# - add save/load function
# - Add config menu (for languages/books)
# - translate to english/make dictionary => Done
# - select which books are available

deutsch = {
            'Stufe':'Stufe',
            'EZM' : 'Entzugsmodifikator: KS+/-',
            'Erf' : 'Erfolge',
            'Schule' : [
                'None',
                'Heilung',
                'Manipulation',
                'Kampf',
                'Illusion',
                'Wahrnehmung'
            ],
            'Trigger' : {
                'Zeit': 1,
                'Berührung': 1,
                'Befehl': 2
            },
            'AlW' : 'Alchemie Würfel',
            'EW' : 'Entzugswiderstand',
            'Ent' : 'Entzug',
            'Dauer' :'Dauer',
            'VerfSp' : 'Verfügbare Sprüche',
            'L+E' : 'Lvl+Erf',
            'Weitere SP' : 'Weitere Sprüche',
            'SP zuf' : "Ausgewählte Sprüche hinzufügen",
            'SpList' : os.path.join(init_dir,'SR_Zauber.txt'),
            'SpDefault' : os.path.join(init_dir,'default_deutsch.spl')
}

english = {
            'Stufe':'Spell Power',
            'EZM' : 'Drain Modifier: SP+/-',
            'Erf' : 'Successes',
            'Schule' : [
                'None',
                'Combat',
                'Detection',
                'Health',
                'Illusion',
                'Manipulation'
            ],
            'Trigger' : {
                'Time': 1,
                'Contact': 1,
                'Command': 2
            },
            'AlW' : 'Alchemy Dice',
            'EW' : 'Drain Resistance',
            'Ent' : 'Drain',
            'Dauer' :'Duration',
            'VerfSp' : 'Available Spells',
            'L+E' : 'Lvl+Suc',
            'Weitere SP': 'Additional Spells',
            'SP zuf' : "Add selected Spell(s)",
            'SpList' : os.path.join(init_dir,'Spelllist_engl.txt'),
            'SpDefault' : os.path.join(init_dir,'default_english.spl')
}

language = english

class SpellFrame():
    #The spell frame consists of two lines:
    #Line 1: Spell Name, School, List of Levels, Link to Street Grimoire
    #Line 2: Drain Modificator, Suffered Drain Damage, Number of Successes
    def __init__(self,zauber,row_count,master):
            self.name = zauber.name
            self.school = zauber.school
            self.master = master
            #First Line
            #generate widgets
            self.lbl_spell = ttk.Label(master=self.master, text = zauber.name)            
            self.lbl_school = ttk.Label(master=self.master, text = zauber.school)
            self.lbl_level = ttk.Label(master=self.master, text = language['Stufe']+":")
            self.ent_lvl_list =ttk.Entry(master=self.master, width=6)
            self.ent_lvl_list.insert(1,zauber.lvls)  
            self.btn_txt = tk.StringVar(value=zauber.reference)
            self.btn_spell_ref= CreateSpellRefButton(master=self.master, zauber=zauber)
           
            #and place them
            self.lbl_spell.grid(row=row_count, column=0, sticky='w',padx=10, pady=1)
            self.lbl_school.grid(row=row_count, column=1, sticky='w',padx=10, pady=1)
            self.lbl_level.grid(row=row_count, column=2, sticky="e",pady=1)
            self.ent_lvl_list.grid(row=row_count, column=3, sticky="w",padx=5,pady=1)
            self.btn_spell_ref.grid(row=row_count, column=4, sticky='ns',padx=5,pady=1)
        
            #Second line
            row_count += 1
            #generate widgets
            self.lbl_drain = ttk.Label(master=self.master, text = language['EZM'])
            self.ent_drain = ttk.Entry(master=self.master, width=3)
            self.ent_drain.insert(0,zauber.drain)
            self.erfolg_list = ttk.Label(master=self.master, text=language['Erf']+": 0")
            self.btn_remove = ttk.Button(master=self.master,text='X', command=self.remove)
                        
            #and place them
            self.lbl_drain.grid(row=row_count, column=0, padx=10,sticky='e',pady=3)
            self.ent_drain.grid(row=row_count, column=1, padx=10, pady=3, sticky='w')
            self.erfolg_list.grid(row=row_count, column=2, columnspan=2, padx=10, pady=3, sticky='w')
            self.btn_remove.grid(row=row_count, column=4, sticky='ns',padx=5,pady=3)
            #add Seperator for next Spell
            row_count +=1
            self.separator = ttk.Separator(master, orient=tk.HORIZONTAL)
            self.separator.grid(column=0, row=row_count, columnspan=5, sticky='new',pady=5)
    
    def removeWidgets(self):
        widgets = [getattr(self,widget) for widget in dir(self) if not widget.startswith('_') 
                   and isinstance(getattr(self,widget), tk.Widget)]
        for widget in widgets:
            if not isinstance(widget,ttk.Frame):
                widget.destroy()
        #self.master.update()
    
    def remove(self):
        #remove the widgets first
        self.removeWidgets()
        #remove the spell from new_spells and spell_var_list
        #TODO: Use only one array to track active spells
        self.master.master.new_spells.remove(self)
        spell_names = [sp.get() for sp in self.master.master.spell_var_list]
        sp_idx = spell_names.index(self.name)
        for spell in self.master.master.spell_list:
            if spell.name == self.name:
                self.master.master.spell_list.remove(spell)
                break
        self.master.master.spell_var_list[sp_idx].set('')
        self.master.update()

class AlchemyDiceFrame(ttk.Frame):
    def __init__(self,master, style, row_count=0, *args, **kw):
        ttk.Frame.__init__(self, master, *args, **kw)
        self.frm_main = master
        self.style = style
        self.row_count = row_count
        #currently, there are only 2 languages, so a Boolean would suffice
        self.language = tk.IntVar()
        self.language.set(language == english)
        #all this is in the default file...
        #but loadLayout needs a draw first...
        """self.ad_settings = {
            "language" : self.language.get(),
            "alchemy dice" : 12,
            "drain resistance" : 12,
            "bonus" : 0,
            "trigger option" : 1
            }
        self.draw()"""
        #load default file
        self.loadLayout(sp_file = language['SpDefault'])
        
        #initialize
        self.trigger_options = language['Trigger']
        self.school_options = language['Schule']
        #default values 

        #self.save_trigger = 1
        #self.save_bonus = 0
        #Add Menubar
        self.menues()
        #self.draw()
        self.update()

    def menues(self):
        top = self.winfo_toplevel()
        self.menuBar = tk.Menu(top)
        top['menu'] = self.menuBar

        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label='Load Spell Setup',accelerator='Ctrl+L',command=self.loadLayout)
        self.bind("<Control-l>", self.loadLayout)
        self.fileMenu.add_command(label='Save Spell Setup',accelerator='Ctrl+S',command=self.saveLayout)
        self.bind("<Control-s>", self.saveLayout)

        self.langMenu = tk.Menu(self.menuBar, tearoff=0)
        self.langMenu.add_radiobutton(label='English',variable=self.language,value=1,command=lambda: self.setLanguage(english))
        self.langMenu.add_radiobutton(label='Deutsch',variable=self.language,value=0,command=lambda: self.setLanguage(deutsch))
        
        self.menuBar.add_cascade(label='File', menu=self.fileMenu)
        self.menuBar.add_cascade(label='Language', menu=self.langMenu)
    
    def setLanguage(self,new_language,load_default = True):
        global language
        global all_spells
        language = new_language
        self.ad_settings["language"] = self.language.get()
        #destroy current window and build anew
        #self.after(1000,self.master.destroy())
        for child in self.winfo_children(): 
            child.destroy()
        #sr_sp_file = language['SpDefault']
        all_sp_file = language['SpList']
        #spell_list= [Spell()]
        #initialize and load langue relevant data
        all_spells = getSpellsFromFile(all_sp_file,sp_attr=["name","school","drain","reference"])
        self.trigger_options = language['Trigger']
        self.school_options = language['Schule']

        #self.spell_list =getSpellsFromFile(sr_sp_file,sp_attr=["name","school","drain","reference","lvls"])
        if load_default:
            self.loadLayout(sp_file = language['SpDefault'])
            #self.draw()
        self.update()

    def saveLayout(self,sp_file = None):
        #Ask for filename and save spell_list to file if not provided
        if sp_file is None:
            sp_file = asksaveasfilename(title='Save Spell Setup:',initialdir=init_dir, defaultextension='.spl', filetypes=[('Spell Setup','*.spl'), ('All files','*.*')]) 
        #save in json format
        json_list = []
        self.ad_settings = {
            "language" : self.language.get(),
            "alchemy dice" : int(self.ent_alch_val.get()),
            "drain resistance" : int(self.ent_dr_resist.get()),
            "bonus" : self.opt_bonus.current(),
            "trigger option" : self.opt_trigger.current()
            }
        json_list.append(self.ad_settings)
        with open(sp_file, 'w', encoding="utf-8") as fp:
            #sp_attr = [attr for attr in dir(Spell()) if not attr.startswith('_')]
            for spell in self.spell_list:
                json_element = [spell.__getattribute__(attr) for attr in dir(Spell()) if not attr.startswith('_')]
                json_list.append(json_element)
            json.dump(json_list, fp)

    def loadLayout(self,sp_file = None):
        #Ask for filename and load spell_list from file
        if sp_file is None:
            sp_file = askopenfilename(title='Save Color Theme:',initialdir=init_dir, defaultextension='.spl', filetypes=[('Spell Setup','*.spl'), ('All files','*.*')])
        #load from json format
        with open(sp_file, 'r', encoding="utf-8") as fp:
            json_list = json.load(fp)
        #get settings first
        self.ad_settings = json_list[0]
        json_list.pop(0)
        self.spell_list=[]
        sp_attr = [attr for attr in dir(Spell()) if not attr.startswith('_')]
        #TODO: use map instead        
        for spell in json_list:
            sp_dummy=Spell()
            for ix, value in enumerate(spell):
                sp_dummy.__setattr__(sp_attr[ix], value)
        
            self.spell_list.append(sp_dummy)
            pass

        #Now that it is loaded, draw it new...
        #remove spells from GUI if they exist
        try:
            for old_spell in reversed(self.new_spells):
                #spell_attr = [attr for attr in dir(old_spell) if not attr.startswith('_')]
                old_spell.removeWidgets()
        except AttributeError:
            pass
        
        if self.ad_settings["language"] == 1:
            loaded_language = english 
        else: 
            loaded_language = deutsch
        
        #set language also draws spells
        self.setLanguage(new_language=loaded_language,load_default=False)
        self.draw()
        #self.drawSpells()    
        #addSpellMenu(self)
        #set the triggers again (this should not be needed, but somehow it is)
        self.opt_trigger.current(self.ad_settings["trigger option"])
        self.opt_bonus.current(self.ad_settings["bonus"])

    def draw(self):
        #draw all frames: Alcemy Dice Frame, Spell Frame, Spell Menu Frame
        #Init values
        def_pady = self.style.def_pady
        #ALchemy dice frame
        self.ad_frame = ttk.Frame(self)
        #self.ad_frame.grid(row=0, rowspan=3, column=0, columnspan = 5, sticky='news')
        self.ad_frame.pack()
        lbl_alch_val = ttk.Label(master=self.ad_frame, text=language['AlW']+":")
        self.ent_alch_val = ttk.Entry(master=self.ad_frame, width="3")
        self.ent_alch_val.insert(1,self.ad_settings["alchemy dice"]) #default value
        lbl_dr_resist = ttk.Label(master=self.ad_frame, text=language['EW']+":")
        self.ent_dr_resist = ttk.Entry(master=self.ad_frame, width="3")
        self.ent_dr_resist.insert(1,self.ad_settings["drain resistance"]) #default value

        #Trigger
        self.opt_trigger_def = tk.StringVar(self)
        self.opt_trigger = ttk.Combobox(self.ad_frame, width=10, textvariable=self.opt_trigger_def, values=list(self.trigger_options.keys()))
        #set default

        lbl_opt_trigger = ttk.Label(master=self.ad_frame, text="Trigger:")
        #Spell Bonus
        self.opt_bonus_def = tk.StringVar(self)
        self.opt_bonus = ttk.Combobox(self.ad_frame, width=10, textvariable=self.opt_bonus_def, values=self.school_options)
        lbl_opt_bonus = ttk.Label(master=self.ad_frame, text="Bonus (+2):")
        #set default
        self.opt_bonus.current(self.ad_settings["bonus"])
        self.opt_trigger.current(self.ad_settings["trigger option"])

        opt_style_def = tk.StringVar(self)
        opt_style_def.set(self.style.theme.name)

        #opt_style =ttk.OptionMenu(self,opt_style_def,*theme_options)
        #btn_get_style = ttk.Button(master=self, text = 'GO!', command=change_style)

        lbl_alch_val.grid(row=self.row_count, column=0, sticky='e', padx=10, pady=def_pady)
        self.ent_alch_val.grid(row=self.row_count, column=1, sticky='w', padx=10, pady=def_pady)
        lbl_dr_resist.grid(row=self.row_count, column=3, columnspan=2, sticky='w', padx=10, pady=def_pady)
        self.ent_dr_resist.grid(row=self.row_count, column=4, sticky='e', padx=10, pady=def_pady)
        #next row
        self.row_count += 1
        lbl_opt_trigger.grid(row=self.row_count, column=0, sticky='e', padx=10, pady=def_pady)
        self.opt_trigger.grid(row=self.row_count, column=1, sticky='w', padx=10, pady=def_pady)
        lbl_opt_bonus.grid(row=self.row_count, column=3, sticky='e', padx=10, pady=def_pady)
        self.opt_bonus.grid(row=self.row_count, column=4, sticky='w', padx=10, pady=def_pady)
        
        self.row_count +=1
        #Add a separator
        separator = ttk.Separator(self.ad_frame, orient=tk.HORIZONTAL)
        separator.grid(column=0, row=self.row_count, columnspan=5, sticky='new',pady=5)
        self.row_count +=1
        
        #spell frame incl. drain
        self.spell_frame = ttk.Frame(self)
        self.spell_frame.pack()
        self.drawSpells()

        #Add Spell menu and button
        self.row_count += 1
        addSpellMenu(self)

        #output frame
        self.output_frame = ttk.Frame(self)
        #self.output_frame.grid(row=2, column=0, columnspan = 4, sticky='news')
        self.output_frame.pack()
        self.row_count += 1
        #frm_out = ttk.Frame(master=window, relief="sunken")
        self.style.configure('New.TButton',font=('Helvetica', 14))

        #print(style.map('TButton',background=[('hover', '!disabled', '#aa00aa')]))
        btn_get_val = ttk.Button(master=self.output_frame, text = 'GO!', command=self.rollDice, style='New.TButton')
        #lbl_check = ttk.Label(master=self, text = 'Anzahl Erfolge: 0',font=('Helvetica', 16))
        self.lbl_damage = ttk.Label(master=self.output_frame, text = language['Ent']+': 0',font=('Helvetica', 14))
        self.lbl_dauer = ttk.Label(master=self.output_frame, text = language['Dauer']+': 0',font=('Helvetica', 14))
        #lbl_check.grid(row=self.row_count, column=0, sticky='w',padx=10, pady=def_pady)
        self.lbl_dauer.grid(row=self.row_count, column=0, sticky='w',padx=10, pady=def_pady)
        self.lbl_damage.grid(row=self.row_count, column=1, sticky='w',padx=10, pady=def_pady)
        btn_get_val.grid(row=self.row_count, column=2, columnspan=2, padx=10, pady=def_pady, sticky='e')

    def addSpell(self):
        #save trigger and bonus before re-drawing
        #self.save_trigger = self.opt_trigger.current()
        #self.save_bonus = self.opt_bonus.current()
        self.ad_settings["trigger option"] = self.opt_trigger.current()
        self.ad_settings["bonus"] = self.opt_bonus.current() 
        #remove spells from GUI
        for old_spell in reversed(self.new_spells):
            #spell_attr = [attr for attr in dir(old_spell) if not attr.startswith('_')]
            old_spell.removeWidgets()
        #then remove everything else
        #for child in self.winfo_children():
        #    child.destroy()
        self.update()
        active_spells = [spell.get() for spell in self.spell_var_list if not spell.get() == '']
        #remove spells from spell list if no longer active
        #and add new active spells to spell list
        for spell in reversed(self.spell_list):
            if spell.name not in active_spells:
                self.spell_list.remove(spell)
            else:
                active_spells.remove(spell.name)
        
        for check_spell in all_spells:
            if check_spell.name in active_spells:
                self.spell_list.append(check_spell) 
        self.drawSpells()    
        #addSpellMenu(self)
        #set the triggers again (this should not be needed, but somehow it is)
        self.opt_trigger.current(self.ad_settings["trigger option"])
        self.opt_bonus.current(self.ad_settings["bonus"])

    def drawSpells(self):
        self.row_count = 3
        self.new_spells=[]

        for zauber in self.spell_list:            
            self.new_spells.append(SpellFrame(zauber,self.row_count,self.spell_frame))
            #spell frame consists of two rows + separator
            self.row_count +=3

    def rollDice(self):
        spell_list = self.new_spells
        #reset drain counter
        self.lbl_damage["text"] = language['Ent']+": 0"
        num_lvl_total= 0
        for index in range(len(self.new_spells)):
            #get number of dice
            num_dice = int(self.ent_alch_val.get())
            #check bonus
            if self.new_spells[index].lbl_school['text'].endswith(self.opt_bonus.get()):
                num_dice += 2

            #get spell level
            #allow for multiple entries (same spell multiple times) with comma seperator
            multi_lvls = spell_list[index].ent_lvl_list.get().split(',')
            #return if empty
            if len(multi_lvls) == 0:
                self.erfolg_list[index]["text"] =""
                continue
            #remove level 0 spells:
            multi_lvls = [zi for zi in multi_lvls if zi.strip().isdigit() and int(zi) !=0]
            #clear level entry
            self.new_spells[index].ent_lvl_list.delete(first= 0, last=100)
            # and write new list
            self.new_spells[index].ent_lvl_list.insert(0, ','.join(multi_lvls))

            if len(multi_lvls) == 0:
                self.new_spells[index].erfolg_list["text"] =""
                continue
            self.new_spells[index].erfolg_list["text"] =language['Erf']+": "
            for sp_ind, single_lvl in enumerate(multi_lvls):
                spell_lvl = int(single_lvl)
                if spell_lvl == 0:
                    self.new_spells[index].ent_lvl_list.delete(first=len(','.join(multi_lvls[:sp_ind])),
                                            last=len(','.join(multi_lvls[sp_ind+1:])))
                    #self.erfolg_list[index]["text"] = self.erfolg_list[index]["text"] +'[0], '
                    continue
                #Add all spell levels for total duration
                num_lvl_total += spell_lvl
                #get drain: drain = spell level +- drain modifier
                drain_mod = int(self.new_spells[index].ent_drain.get())
                #add drain modifier from trigger
                drain_trig = self.trigger_options.get(self.opt_trigger.get())
                total_drain = spell_lvl + drain_mod + drain_trig
                #Minimum Drain: 2
                total_drain = max(total_drain, 2)
                #TODO: add ingrediences
                num_success = numSuccesses(num_dice)
                #limit (without ingredients)
                num_success = min(num_success,spell_lvl)
                num_spell = numSuccesses(spell_lvl)
                num_total = num_success - num_spell
                #Entzugswiderstand
                self.entzug(num_total,total_drain, index)

            self.new_spells[index].erfolg_list["text"] = self.new_spells[index].erfolg_list["text"][:-2]
        #total duration
        self.lbl_dauer["text"] =language['Dauer']+": " + str(num_lvl_total)

        #generate the output
        self.generateOutputGui()
    #end def rollDice():

    def entzug(self,num_total, total_drain, index):
        #calculate and output drain
        dr_roll= int(self.ent_dr_resist.get())
        #AUtomatische Erfolge 1 pro 4 würfel
        if int(dr_roll/4) < total_drain:
            dr_res = numSuccesses(dr_roll)
        else:
            dr_res = int(dr_roll/4)

        #Verbleibender Entzug
        dr_dmg = max(0, total_drain - dr_res)
        self.new_spells[index].erfolg_list["text"] += str(num_total) +" (" + str(dr_dmg)+"), "

        dr_dmg= dr_dmg + int(self.lbl_damage["text"][7:])
        #total drain damage
        self.lbl_damage["text"] = language['Ent']+": " + str(dr_dmg)

    def generateOutputGui(self):
        op_frame=OutputGui(spell_list=self.new_spells,frame=self)
        #ttk.Toplevel().update()


class OutputGui():
    def __init__(self,spell_list,frame):
        top = ttk.Toplevel()
        self.frame=ttk.Frame(top)
        self.frame.grid(row=0,column=0)
        top.title(language['VerfSp'])
        #top left corner of new window is top right corner of first window +10px in x
        gm='+' + str(frame._root().winfo_x()+frame.winfo_width()+10) +'+' + str(frame._root().winfo_y())
        top.geometry(gm)
        vari=[tk.IntVar()]
        rb_spell=[ttk.Checkbutton()]
        for index, zauber in enumerate(spell_list):
            #use only spells, that have levels
            if len(zauber.ent_lvl_list.get()) == 0:
                continue
            lbl_spell = ttk.Label(self.frame, text = zauber.name)
            lbl_spell.grid(row=index,column=0,sticky='w', pady=10, padx=10)

            #rb_dummy=(ttk.Checkbutton(self, text="Lvl+Erf = "+ent_lvl_list[index].get(),variable=vari[index], onvalue=index, offvalue=-index))
            for col, lvl in enumerate(zauber.ent_lvl_list.get().split(',')):
                #should be redundant, as num decimal levels have been eliminated before
                if not lvl.strip().isdecimal():
                    continue
                erfolge=zauber.erfolg_list['text'].split()
                lvl_list=zauber.ent_lvl_list.get().split(',')
                rb_dummy=CreateCB(self.frame,index,col,lvl_list=lvl_list,erf_num=erfolge,)
                rb_spell.append(ttk.Checkbutton)
                vari.append(tk.IntVar())
                rb_spell[index]=rb_dummy
                #rb_spell[index].configure(command=spell_used(index))
                rb_spell[index].grid(row=index,column=col+1,sticky='w', pady=10, padx=10)
                #rb_dummy.grid(row=index,column=1,sticky='w', pady=10, padx=10)
                vari[index].set(-index)

class CreateCB(ttk.Checkbutton):
    def __init__(self, parent, rownum,colnum=0,lvl_list=[],erf_num='',*args, **kwargs):
        super().__init__(parent,*args,**kwargs)
        #self.master=parent
        self.parent=parent
        self.variable = tk.StringVar(self)
        self.config(variable=self.variable)

        if  int(lvl_list[colnum]) < 1 or int(erf_num[(colnum)*2+1]) <1:
            self.state(('disabled','selected'))
        self.config(text=language['L+E']+" = "+lvl_list[colnum].strip()+"+"+erf_num[(colnum)*2+1],
                    onvalue=str(rownum)+', '+str(colnum+1),
                    offvalue='off',
                    command=self.spell_used)
        self.grid(row=rownum,column=colnum+1,sticky='w', pady=10, padx=10)

    def spell_used(self):
         self.state(('disabled','selected'))

def addSpellMenu(master):
    #TODO make class not function or put under AlchemyDiceFrame
    global all_spells
    #add frame
    master.spm_frame = ttk.Frame(master)
    master.spm_frame.pack()
    
    #generate the fields to add spells
    menubutton = ttk.Menubutton(master=master.spm_frame,text=language['Weitere SP'],direction='above')
    btn_add_spell = ttk.Button(master=master.spm_frame, text = language['SP zuf'], command=master.addSpell)
    sp_menu = tk.Menu(menubutton, tearoff=0)
    menubutton.grid(row=master.row_count, column=0, columnspan=2, padx=10, sticky='we')       
    btn_add_spell.grid(row=master.row_count, column=2, columnspan=1, padx=10, sticky='e')
    
    #TODO: Keep Menu open after click
    master.spell_var_list = []
    master.school_var_list = []
    spell_menu_list =[]
    sml_index = 0
    used_spells = [spell.name for spell in master.new_spells]
    #cascade it by school
    for school in master.school_options:
        if school == 'None':
            continue
        spell_menu=tk.Menu(sp_menu, tearoff=0, title=school)
        master.school_var_list.append(tk.IntVar())
        master.school_var_list[-1].set(sml_index)
        for spell in all_spells:
            master.spell_var_list.append(tk.StringVar())
            if spell.school.lower() == school.lower():
                spell_menu.add_checkbutton(label=spell.name,onvalue=spell.name,variable = master.spell_var_list[-1], 
                                           command=lambda: keep_menu_open(spell_menu_list,master.school_var_list[-1]))  
        
                #check active spells
                if spell.name in used_spells:
                    master.spell_var_list[-1].set(spell.name)
        spell_menu_list.append(spell_menu)
        
        # Add each school as a seperate menu in the cascade
        sp_menu.add_cascade(label=school, menu =spell_menu, 
                           command=lambda: openMenu(master.school_var_list[-1]))
        #sp_menu.bind("<Button-1>",lambda e: keep_menu_open(e,sp_menu))
        #sp_menu.bind("<ButtonRelease-1>",lambda: keep_menu_open(sp_menu,sp_menu.winfo_x,sp_menu.winfo_y))
        sml_index += 1
    menubutton['menu'] = sp_menu

    def keep_menu_open(menu_list,index_var):
        index = index_var.get()
        menubutton.event_generate("<Button-1>")  # Programmatically reopens the menu
        sp_menu.event_generate("<Button-1>",x=10,y=30) 
        #print('keep open:',sp_menu.winfo_x(),sp_menu.winfo_y(),sp_menu.winfo_rootx(),sp_menu.winfo_rooty(),index)

    # Bind the <Leave> event to close the menu when the mouse moves away
    def closeMenu(event):
        sp_menu.unpost()

    def openMenu(index):
        #index = 2
        spell_menu_list[index].post(sp_menu.winfo_x(), sp_menu.winfo_y())
        #print('openmenu:',index,sp_menu.winfo_x(), sp_menu.winfo_y())

def reconfigureFrame(frm_main, spell_list):
    #move half of spells in next column
    grid_size=frm_main.grid_size()
    #leave top rows
    top_bottom_rows=2
    #number of spells to be shifted to right column
    move_over = int((len(spell_list))/2)
    #number of spells remaining left
    remain = len(spell_list)-move_over

    for widget in frm_main.winfo_children():
        try:
            wid_row = widget.grid_info()['row']
            #all spells
            if wid_row >= remain*2+top_bottom_rows:
                if wid_row == grid_size[1]-1:
                    wid_row+=1
                    widget.grid(row=remain*2+top_bottom_rows,
                                column=widget.grid_info()['column']+grid_size[0])
                else:
                    widget.grid(row=wid_row-remain*2, 
                            column=widget.grid_info()['column']+grid_size[0])

        except:
            print('Exception:',widget.winfo_class())
            print(dict(widget))

def numSuccesses(num_dice = 0):
    num_success = 0
    for a in range(1,num_dice):
        wurf = random.randint(1,6)
        if wurf >= 5:
            num_success +=1

    return num_success
# end def numSuccesses(num_dice = 0):

"""def get_default_from_file(filename):
    sp_list =[Spell()]
    #sp_attr = [ attribute for attribute in dir(Spell()) if not attribute.startswith('__')]
    sp_attr=["name","school","drain","reference","lvls"]

    f = open(filename, "rt")
    for index, spell_line in enumerate(f):
        for ix, value in enumerate(spell_line.split(';')):
            sp_list[index].__setattr__(sp_attr[ix], value)
        sp_list.append(Spell())
    sp_list.pop(-1)
    f.close()
    return sp_list"""

def getSpellsFromFile(filename,sp_attr):
    #load complete spell list or default setup from txt file
    sp_list =[Spell()]

    f = open(filename, "r", encoding="utf-8")
    for index, spell_line in enumerate(f):
        for ix, value in enumerate(spell_line.strip().split(';')):
            sp_list[index].__setattr__(sp_attr[ix], value)
        sp_list.append(Spell())
    sp_list.pop(-1)
    f.close()
    return sp_list

class CreateSpellRefButton(ttk.Button):
    def __init__(self, master, zauber, *args, **kwargs):
        super().__init__(master,*args,**kwargs)
        self.master=master
        self.zauber=zauber
        self.ref=tk.StringVar(self)
        self.ref.set(self.zauber.reference)
        self.configure(textvariable=self.ref,
                       command=lambda: self.openSpellbook(self.zauber.reference))
        #self.button = ttk.Button(master=frm_main, textvariable=btn_txt, 
        #command=lambda: print(z_ref,z_ref[index],index)) 
        #command=lambda: self.openSpellbook(zauber.reference))  

    def openSpellbook(self,spell_ref):
        ref_file=spell_ref.split()[0].strip()
        page=int(spell_ref.split()[1])    
        #page numbers are not acutal pdf page numbers, so add pages per book
        add_pages = {
            "SG" : 2,
            "SR5" : 2
        }
        page  += add_pages[ref_file]
        #print(ref_file,page)
        #path_to_acrobat = os.path.abspath(r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe")
        book_path = {
            "SG" : os.path.join(pdf_dir,r"DE\Shadowrun_5D_-_Strassengrimoire.pdf"),
            "SR5" : os.path.join(pdf_dir,r"Core\Shadowrun 5e - Core Rulebook (2nd Printing).pdf")
            }
        process = subprocess.Popen([path_to_acrobat, '/A','page='+str(page), book_path[ref_file]], shell=False, stdout=subprocess.PIPE) 
  
class Spell():

    def __init__(self, name='default', school='Wahrnehmung', drain=-2, reference='SR5 280', lvls=4):
        self.name = name
        self.school = school
        self.drain = drain
        self.reference = reference
        self.lvls = lvls

    def __str__(self):
        return f"{self.name}, {self.school}, ({self.drain}),{self.reference},{self.lvls}"

def main():

    global all_spells

    window = tk.Tk()
    window.title("An Alchemist's Tool "+Version+"\t"+chr(169)+" 2024/25 by Shivkala")
    #window.geometry('500x560')
    #frm_main = ttk.Frame(master=window,height=600)

    style =ttk.Style('vapor')
    theme_options = style.theme_names()

    style.configure('.', font=('Helvetica',9))
    style.def_pady=5

    style.map('TButton',
        foreground=[('pressed', 'blue'),
                    ('active', 'red')],
        background=[('active','blue')])
    style.map('TEntry',
        background=[('pressed', 'blue'),
                    ('active', 'red')])
    row_count= 0
    #font_size = font.nametofont('TkDefaultFont')["size"]
    #Draw the Frame
    al_dice_frm = AlchemyDiceFrame(window,style,row_count)
    #al_dice_frm.draw()
    #al_dice_frm.update()
    #show all
    al_dice_frm.grid(row=0,column=0)
    window.update()
    if window.winfo_height() > window.winfo_screenheight()*0.9:
        reconfigureFrame(al_dice_frm, al_dice_frm.spell_list)

    window.mainloop()

if __name__ == '__main__':
    main()