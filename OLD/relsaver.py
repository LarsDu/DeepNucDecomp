import numpy as np
import os
import h5py
from Bio import SeqIO

"""
This file contains classes useful for saving relevance data as
either tab delimited text files or hdf5 files.
"""


#Debug
#Write Hdf5Saver lookup functions




class Extractor:

    @staticmethod
    def retrieve_headers(input_file):
        fext = os.path.splitext(input_file)[1]
        if fext == '.fa' or fext =='.fasta':
            return Extractor.headers_from_fasta(input_file)
        elif fext == '.txt':
            lines = None
            with open(input_file, 'rU') as rf:
                lines = [line.rstrip() for line in rf]
            return lines
    
    @staticmethod
    def headers_from_fasta(fname):
        seq_ids= []
        #Get all headers from a fasta file in sequential order
        with open(fname,'rU') as infile:
            for sequence in SeqIO.parse(infile,"fasta"):
                seq_ids.append(sequence.id)
        return seq_ids

    
class Hdf5Extractor(Extractor):
    def __init__(hdf5_data_file,seq_len,headers_file=None):
        '''
        Extract data generated by Hdf5 saver by index,
        or by looking up header name

        Headers file can be fasta or a simple text file
        '''
        
        self.headers_file = headers_file
        self.data_file = hdf5_data_file
        self.headers = Extractor.retrieve_headers(self.headers_file)
        
        
    def lookup_ind(self):
        #TODO
        pass
        
        
class TextExtractor(Extractor):
    def __init__(text_data_file,seq_len,headers_file=None):
        '''
        Extract data generated by Hdf5 saver by index,
        or by looking up header name
        '''
        self.headers_file = headers_file
        self.data_file = self.text_data_file
        self.headers = Extractor.retrieve_headers(self.headers_file)

    def lookup_index(self,index):
        
        '''
        Lookup a relevance entry by index (line number in this case)
        '''
        with open (self.data_file,'r') as rf:
            for i,line in enumerate(rf):
                if i == index:
                    cur_line = line.rstrip().split(',')
                    data = cur_line[:-1]
                    label = cur_line[-1]
                    return (data,label)

    def lookup_header(self,query):
        ind = self.lookup_header_index(query)
        return self.lookup_index(ind)
    
        
    def lookup_header_index(self,query):
        with open (self.header_file,'r') as hf:
            for ind,line in enumerate(hf):
                cur_header = line.rstrip().split()
                for word in cur_header:
                    if word == query:
                        return ind
        

        
class Hdf5RelSaver:
    def __init__(self,save_file,seq_len,num_records,key='relevances'):
        self.filename = save_file
        self.seq_len = seq_len
        self.num_entries = num_records
        self.key = key
        #self.num_classes = num_classes
        #File handle
        self.fhandle = None # call open() to set this
        self.dset=None

        
        
    def write(self,data,label):
        #Writes one entry at a time to self.filename
        #Flatten data and label (note: label should just be a single value!)
        #TODO make label a single value
        label_number =label.tolist().index(1.)#Convert from one-hot to single number
        if len(label_number !=1):
            print "Error in label conversion in Hdf5Saver.write()"
        dset[cur_row,:] = np.concatenate(np.ravel(data),label_number,axis=0)
        
    def open(self):
        self.fhandle = h5py.File(self.filename,'w')
        self.fhandle.attrs['seq_len'] = self.seq_len
        num_rows = self.seq_len*4+1
        num_cols = self.num_records
        self.dset = self.fhandle.create_dataset(self.key,
                                           (num_rows,num_cols),
                                           compression = 'gzip',
                                           maxshape= (1000000,num_cols))
        
        #self.fhandle.attrs['num_classes'] = self.num_classes
        
    def close(self):
        self.fhandle.close()


        
class TextRelSaver:
    def __init__(self,save_file,seq_len):
        self.filename = save_file
        self.seq_len=seq_len
        #self.num_classes = num_classes
        #File handle
        self.fhandle = None

    def write(self,data,label):
        #Make sure file is open first
        entry = np.concatenate(np.ravel(data),np.ravel(label),axis=0)
        np.savetxt(entry,self.fhandle,delimiter=',')

        
        pass
    
    def open(self):
        self.fhandle = open(self.filename,'w')
        
    def close(self):
        self.fhandle.close()
        
