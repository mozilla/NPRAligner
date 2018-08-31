import os
import glob
import pathlib
import logging
import multiprocessing
import xml.etree.ElementTree as ET

import gentle

disfluencies = set(['uh', 'um'])

nthreads = multiprocessing.cpu_count()

source_glob_suffix = '*/raw/transcripts/extracted/*/*/*.xml'
source_glob_prefix = '/snakepit/shared/data/NPR/WAMU'

target_prefix = '/snakepit/uploads/NPR/WAMU'

namespaces = {'vx' : 'http://www.voxant.com/NewsML/transcript'}

glob_path = os.path.join(source_glob_prefix, source_glob_suffix)

resources = gentle.Resources()

def on_progress(p):
    for k,v in p.items():
        print("%s: %s" % (k, v))

for source_path_xml in glob.glob(glob_path, recursive=True):
    target_path_txt = os.path.join(target_prefix, os.path.relpath(source_path_xml, source_glob_prefix)).replace('.xml', '.txt')
    pathlib.Path(os.path.dirname(target_path_txt)).mkdir(parents=True, exist_ok=True)
    with open(target_path_txt, 'w+') as target_file_txt:
        parsed_source_xml = ET.parse(source_path_xml)
        parsed_root = parsed_source_xml.getroot()
        for turn in parsed_root.findall('.//vx:Turn', namespaces):
            if 'DISCLAIMER' != turn.attrib['Speaker']:
                for fragment in turn.findall('.//vx:Fragment', namespaces):
                    target_file_txt.write(fragment.text)

    with open(target_path_txt) as target_file_txt:
        transcript = target_file_txt.read()

    source_path_mp3 = source_path_xml.replace('transcripts/extracted', 'audio').replace('.xml', '.mp3')
    if os.path.isfile(source_path_mp3) and transcript:
        target_path_json = target_path_txt.replace('.txt', '.json')
        with open(target_path_json, 'w') as target_file_json:
            print('converting audio to 8K sampled wav')
            with gentle.resampled(source_path_mp3) as wavfile:
                print('starting alignment for', source_path_xml, ' and ', source_path_mp3)
                aligner = gentle.ForcedAligner(resources, transcript, nthreads=nthreads, disfluency=False, conservative=False, disfluencies=disfluencies)
                result = aligner.transcribe(wavfile, progress_cb=on_progress, logging=logging)
                target_file_json.write(result.to_json(indent=2))
        print('finished alignment in', target_path_json)
