from transformers import BertTokenizer, BertForSequenceClassification
import torch
import os


label_dict = {'Band-6': 0, 'Band-7': 1, 'Band-8': 2}


def get_device():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    return device


def get_model():

    model = BertForSequenceClassification.from_pretrained("bert-base-uncased",
                                                          num_labels=len(label_dict),
                                                          output_attentions=False,
                                                          output_hidden_states=False)

    return model


def tokenize(text):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
    encoded_data = tokenizer.batch_encode_plus(
        text,
        add_special_tokens=True,
        return_attention_mask=True,
        padding='max_length',
        max_length=318,
        truncation=True,
        return_tensors='pt'
    )

    return encoded_data


def run_evaluation(inputs):

    data = tokenize(inputs)

    # model_file = os.path.join(os.getcwd(), "predictor/data_files/model.model")
    model_file = os.path.join(os.getcwd(),"predictor/data_files/model.model")


    model = get_model()
    # model.to(get_device())
    model.load_state_dict(torch.load(model_file, map_location=torch.device('cpu')))

    model.eval()

    with torch.no_grad():
        logits = model(**data).logits

    predicted = logits.argmax().item()

    return predicted
