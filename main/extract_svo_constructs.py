# coding=utf-8
from typing import List

from spacy.tokens.span import Span
from spacy.tokens.token import Token

import main.utils as utils
from main.consts import Consts
from main.objects.participant import Participant
from main.objects.svoconstruct import SvoConstruct


def extract_svo_constructs(sentence: Span, participants: List[Participant]) -> List[SvoConstruct]:
    """
    Function for extracting svos from sentence
    """
    tmp_output = []
    root = sentence.root
    nsubj_list = utils.find_tokens_with_dependencies_for_token_in_subtree(root, ["nsubj"])
    nsubjpass_list = utils.find_tokens_with_dependencies_for_token_in_subtree(root, ["nsubjpass"])
    if len(nsubj_list) > 0:
        for token in nsubj_list:
            subject = token
            verb = subject.head
            output_obj = find_token_in_children(verb, ["dobj", "attr"])
            if output_obj is None:
                output_obj = find_token_in_ancestors(verb, ["dobj", "iobj", "pobj", "attr", "xcomp"])
            if subject is not None and verb is not None:
                svo = SvoConstruct(subject=subject, verb=verb, new_object=output_obj, position=verb.i)
                if len(tmp_output) > 0:
                    if check_if_svo_is_unique(svo, tmp_output):
                        tmp_output.append(svo)
                else:
                    tmp_output.append(svo)

    if len(nsubjpass_list) > 0:
        for token in nsubjpass_list:
            subject = token
            verb = subject.head
            if subject is not None and verb is not None:
                svo = SvoConstruct(subject=subject, verb=verb, position=verb.i)
                if len(tmp_output) > 0:
                    if check_if_svo_is_unique(svo, tmp_output):
                        tmp_output.append(svo)
                else:
                    tmp_output.append(svo)

    # Check if conjunction exists in sentence and extract possible SVO
    for token in sentence:
        if token.dep_ == "conj" and token.pos_ == "VERB":
            output_obj = find_token_in_children(token, ["dobj", "attr", "ccomp"])
            if output_obj is None:
                output_obj = find_token_in_ancestors(token, ["dobj", "iobj", "pobj", "attr", "ccomp", "xcomp"])
            subject = find_subject_for_conjunction(token)

            if subject is not None and token is not None:
                svo = SvoConstruct(subject=subject, verb=token, new_object=output_obj, position=token.i)
                if len(tmp_output) > 0:
                    if check_if_svo_is_unique(svo, tmp_output):
                        tmp_output.append(svo)
                else:
                    tmp_output.append(svo)

    # Check if extracted svo can be assigned to verified participant
    assign_svo_to_participant(tmp_output, participants)
    return tmp_output


def find_token_in_ancestors(token: Token, dependencies_set):
    if token.dep_ in dependencies_set:
        return token
    else:
        for child in token.children:
            if child.dep_ in dependencies_set:
                return child
            elif child.dep_ in Consts.skippable_dependencies_list:
                output = find_token_in_ancestors(child, dependencies_set)
                if output is not None:
                    return output
    return None


def find_token_in_children(token: Token, dependencies_set):
    if token.dep_ in dependencies_set:
        return token
    else:
        for child in token.children:
            if child.dep_ in dependencies_set:
                return child
    return None


def check_if_svo_is_unique(svo: SvoConstruct, svos: List[SvoConstruct]):
    for tmp_svo in svos:
        if svo.get_verb() == tmp_svo.get_verb() \
                and svo.get_object() == tmp_svo.get_object():
            return False
    return True


def assign_svo_to_participant(svos: List[SvoConstruct], participants: List[Participant]):
    for svo in svos:
        for participant in participants:
            if participant.get_participant_token() == svo.get_subject():
                svo.set_participant(participant)


def find_subject_for_conjunction(conjunction: Token):
    return find_token_in_children(conjunction.head, ["nsubj", "nsubjpass", "compound"])
