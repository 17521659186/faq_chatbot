#!/usr/bin/env python
# coding:utf-8
import json
import os
import re

import yaml
from rasa_nlu.training_data import Message
from rasa_nlu.training_data import TrainingData


class TrainDataReader:
    def __init__(self, path_context):
        self.path_context = path_context

    def gen_nlp_train_script(self, intents, entities, settings={"store_entities_as_slots": True}, manual_stories={}):
        intent_names = []
        templates = {}
        stories = []
        actions = set()
        dbs = {}
        remotes = {}

        config = {
            "store_entities_as_slots": True
        }

        slots = dict(map(lambda entity: (entity, {"type": "text"}), entities))

        for intent in intents:
            intent_names.append(intent["name"])
            if intent["name"] != "None":
                if "action" in intent:
                    action = intent["action"]
                else:
                    action = {
                        "table_name": None,
                        "positive": ["当前意图是： " + intent["name"]]
                    }
                if "conditions" in action:
                    action_name = "db_" + intent["name"]
                    dbs[action_name] = {"conditions": action["conditions"]}
                    actions.add(action_name)
                elif "remote_url" in action and action["remote_url"]:
                    action_name = "remote_" + intent["name"]
                    remotes[action_name] = {"remote_url": action["remote_url"],
                                            "params_entities": action["params_entities"]}
                    actions.add(action_name)
                else:
                    action_name = "utter_" + intent["name"]
                    actions.add(action_name)
                    templates[action_name] = action["positive"]

                if not manual_stories or (
                                manual_stories and "ignores" in manual_stories and intent["name"] not in manual_stories[
                            "ignores"]):
                    stories.append((intent["name"], action_name))
            else:
                actions.add("chat")
                stories.append(("None", "chat"))

        if manual_stories and "actions" in manual_stories:
            for item in manual_stories["actions"]:
                actions.add(item)

        domain = {
            "slots": slots,
            "entities": list(entities),
            "intents": intent_names,
            "templates": templates,
            "actions": list(actions),
            "config": config,
            "dbs": dbs,
            "remotes": remotes,
            "settings": settings
        }

        if not os.path.exists(os.path.dirname(self.path_context.nlp_yaml_path)):
            os.makedirs(os.path.dirname(self.path_context.nlp_yaml_path))
        with open(self.path_context.nlp_yaml_path, "w") as f:
            yaml.safe_dump(domain, f, allow_unicode=True, default_flow_style=False)

        stories = list(map(lambda story: "\n".join(["##", "* " + story[0], " - " + story[1]]), stories))

        if manual_stories and "stories" in manual_stories:
            for item in manual_stories["stories"]:
                stories.append(item["story"])

        if not os.path.exists(os.path.dirname(self.path_context.nlp_stories_path)):
            os.makedirs(os.path.dirname(self.path_context.nlp_stories_path))

        with open(self.path_context.nlp_stories_path, "w") as f:
            for story in stories:
                f.writelines(story + "\n")

    @staticmethod
    def is_template(config):
        try:
            _config = json.loads(config)
            return _config
        except ValueError as e:
            return None

    def read_from_json(self):
        if os.path.exists(self.path_context.nlu_train_path):
            with open(self.path_context.nlu_train_path, "r",encoding='utf-8') as f:
                js = json.load(f)

            training_examples = []
            regex_features = []
            phrase_list = {}
            external_features = []
            user_dict = []
            regex_entities = {}
            patterns_intent = {}
            entity_names = set()
            entity_synonyms = {}

            # Simple check to ensure we support this luis data schema version
            # Process entities
            for r in js.get("regex_entities", []):
                entity_name = r.get("name")
                pattern = r.get("regexPattern")
                entity_names.add(entity_name)
                regex_entities[entity_name] = pattern

            if not os.path.exists(os.path.dirname(self.path_context.entity_regex_path)):
                os.makedirs(os.path.dirname(self.path_context.entity_regex_path))
            with open(self.path_context.entity_regex_path, "w") as f:
                json.dump(regex_entities, f, ensure_ascii=False)



            for r in js.get("entities", []):
                entity_name = r.get("name")
                entity_names.add(entity_name)

            for r in js.get("closed_entities", []) if "closed_entities" in js else js.get("closedLists", []):
                entity_name = r.get("name")
                entity_names.add(entity_name)
                phrase_list[entity_name] = []
                sub_lists = r.get("subLists")
                for item in sub_lists:
                    user_dict.append(item["canonicalForm"])
                    phrase_list[entity_name].append(item["canonicalForm"])
                    if item["list"]:
                        user_dict += item["list"]
                        for item_item in item["list"]:
                            entity_synonyms[item_item] = item["canonicalForm"]
                            phrase_list[entity_name].append(item_item)

            for r in js.get("model_features", []):
                name = r.get('name')
                words = r.get('words').split(",")
                external_features.append(dict(map(lambda word: (word, name), words)))

            if not os.path.exists(os.path.dirname(self.path_context.external_feature_path)):
                os.makedirs(os.path.dirname(self.path_context.external_feature_path))
            with open(self.path_context.external_feature_path, "w") as f:
                json.dump(external_features, f, ensure_ascii=False)

            # Process intents
            intents = js.get("intents")

            # Process pattern intent
            for r in js.get("patterns"):
                pattern = r["pattern"]
                intent = r["intent"]
                res = re.findall(r"{(.+?)}", pattern)
                pattern = pattern.replace("]", "]*")
                keys = "-".join(sorted(res))
                if keys not in patterns_intent:
                    patterns_intent[keys] = [(intent, pattern)]
                else:
                    patterns_intent[keys].append((intent, pattern))

            if not os.path.exists(os.path.dirname(self.path_context.patterns_intent_path)):
                os.makedirs(os.path.dirname(self.path_context.patterns_intent_path))
            with open(self.path_context.patterns_intent_path, "w") as f:
                json.dump(patterns_intent, f, ensure_ascii=False)

            if not os.path.exists(os.path.dirname(self.path_context.entity_list_path)):
                os.makedirs(os.path.dirname(self.path_context.entity_list_path))
            with open(self.path_context.entity_list_path, "w",encoding='utf-8') as f:
                json.dump(phrase_list, f, ensure_ascii=False)

            self.dump_user_dict(user_dict)

            for s in js["utterances"]:
                text = s.get("text")
                intent = s.get("intent")
                entities = []
                for e in s.get("entities") or []:
                    start, end = e["startPos"], e["endPos"] + 1
                    val = text[start:end]
                    entities.append({"entity": e["entity"],
                                     "value": val,
                                     "start": start,
                                     "end": end})

                data = {"entities": entities}
                if intent:
                    data["intent"] = intent
                training_examples.append(Message(text, data))

            ## genenrate_domain
            settings = js.get("settings", {})
            self.gen_nlp_train_script(intents, entity_names, js.get("settings", {}))
            if settings:
                dir_name = os.path.dirname(self.path_context.settings_path)
                if not os.path.exists(dir_name):
                    os.makedirs(dir_name)
                with open(self.path_context.settings_path, "w") as f:
                    json.dump(settings, f)

            return (
                TrainingData(training_examples, entity_synonyms=entity_synonyms, regex_features=regex_features),
                settings)
        else:
            return None, None

    @staticmethod
    def load_data(train_data_input_path, mode_output_path):
        reader = TrainDataReader(train_data_input_path, mode_output_path)
        reader.read_from_json()

    def dump_user_dict(self, list_entities):
        if not os.path.exists(os.path.dirname(self.path_context.jieba_user_dict_path)):
            os.makedirs(os.path.dirname(self.path_context.jieba_user_dict_path))

        with open(self.path_context.jieba_user_dict_path, "w",encoding='utf-8') as f:
            f.write("\n".join(list_entities))


if __name__ == "__main__":
    pass
