import argparse
from typing import Tuple

from optimizer.core.prompt_optimizer_fewshot import PromptOptimizer
from llm.llm_config import LLM_Config
import yaml


def parse_args():
    parser = argparse.ArgumentParser(description="PromptOptimizer CLI")

    # LLM parameter
    parser.add_argument("--opt-model", type=str, default="deepseek-r1", help="Model for optimization")
    parser.add_argument("--opt-temp", type=float, default=0.7, help="Temperature for optimization")
    parser.add_argument("--eval-model", type=str, default="deepseek-r1", help="Model for evaluation")
    parser.add_argument("--eval-temp", type=float, default=0.3, help="Temperature for evaluation")
    parser.add_argument("--exec-model", type=str, default="deepseek-r1", help="Model for execution")
    parser.add_argument("--exec-temp", type=float, default=0.4, help="Temperature for execution")

    # PromptOptimizer parameter
    parser.add_argument("--workspace", type=str, default="../../results", help="Path for optimized output")
    # parser.add_argument("--current_round", type=int, default=1, help="Initial round number")
    # parser.add_argument("--max-rounds", type=int, default=10, help="Maximum number of rounds")
    # parser.add_argument("--template", type=str, default="SummaryCJ.yaml", help="Template file name")
    # parser.add_argument("--name", type=str, default="SummaryCJ", help="Project name")

    return parser.parse_args()


def load_config(config_path: str) -> dict:
    """从 YAML 文件加载配置"""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def create_llm_config_from_yaml(
        config: dict,
        model_name: str,
        temperature: float
) -> LLM_Config:
    """
    根据 YAML 中的配置创建 LLM_Config 实例
    - 如果指定了 model_name，则从 models 字段中读取
    - 否则使用全局 llm 字段作为默认配置
    """

    if model_name in config.get("models", {}):
        model_config = config["models"][model_name]

    else:
        # 使用默认
        model_config = config["llm"]

    return LLM_Config(
        model_name=model_name,
        api_key=model_config["api_key"],
        base_url=model_config["base_url"],
        temperature=temperature
    )


# 启动第一轮优化
def start_optimization(optimizer, current_prompt, qa_list) -> Tuple[str, str, str, str, bool]:

    modification_all, anaysis_all, new_prompt, new_answer, success = optimizer.optimize_first(current_prompt, qa_list)

    return modification_all, anaysis_all, new_prompt, new_answer, success


# 继续优化
def continue_optimization(optimizer, modification_all: str, anaysis_all:str, last_answer, last_prompt, qa_list) -> tuple[str, str, str, str, bool]:
    # 调用下一轮优化
    modification_all, anaysis_all, new_prompt, new_answer, success = optimizer.optimize_next(modification_all, anaysis_all, last_answer, last_prompt, qa_list)

    return modification_all, anaysis_all, new_prompt, new_answer, success

if __name__ == "__main__":
    args = parse_args()

    config = load_config("../../llm/config.yaml")

    # 构建 LLM 配置
    optimize_config = create_llm_config_from_yaml(config, args.opt_model, args.opt_temp)
    evaluate_config = create_llm_config_from_yaml(config, args.eval_model, args.eval_temp)
    execute_config = create_llm_config_from_yaml(config, args.exec_model, args.exec_temp)

    # 初始化优化、执行、评估反思三阶段优化器设置
    optimizer = PromptOptimizer(
        optimize_llm_config=optimize_config,
        evaluate_llm_config=evaluate_config,
        execute_llm_config=execute_config,
        # rounds=args.current_round,
        # optimized_path=args.workspace,
        # template=args.template,
        # name=args.name
    )
    current_prompt = """
    分析一下上面这通催收员与债务人的电话催收录音转文字记录，你需要推理并填写一个催记表单。表单有11项要素需要你依次填写内容或从枚举值中选择选项，11项要素如下：
  1.沟通对象：本人、配偶、共借人、共借人配偶、保证人、朋友
  2.沟通结果：（催收沟通的具体结果）已还款、承诺还款、协商未果、还款能力不足/意愿不足、投诉、转分行协商、客户非本人、否认贷款、响铃未接/响铃挂断/占线、关机/停机/不在服务区/呼叫受限、空号
  3.承诺还款金额：（沟通结果是承诺还款时填写要还的逾期金额）
  4.承诺还款日期：（沟通结果是承诺还款时填写要还的逾期金额）
  5.特殊催收处理：确认虚假按揭、欺诈、死亡、不良资产处理中、失联、其他特殊催收处理
  6.最佳联系时段：
  7.跟进时间：
  8.客户态度：平静、友好、愤怒、愧疚、绝望、投诉倾向、自杀倾向、未获取
  9.逾期原因：外部策略影响、自然灾害出现重大变故（含交通事故/婚姻变更/重病/亡等情形）、被冒名/被欺诈还款能力下降（含失业/工作变动/收入福利下降等）职工人士、银行抽贷、民间借贷、对外担保代偿、改变贷款用途、经营不善（自营人士）、法律纠纷/涉诉等（含抵押物交付纠纷等）、不良嗜好、恶意拖欠、未获取、其他
  10.下一步建议举措：继续正常催收、提前现场催收、推进司法催收、客户经理协助、转委外催收、合作方代偿定期提醒、敏感客户降低催收频次
  11.催收备注：（需要自由发挥，例如客户称本月还款/客户已经离婚，房子判给前夫，前夫姓名xxx，电话xxxx/客户不接电话/未发工资等）
  以上第1/2/5/8-10条均只能从列出的枚举值中选择（每一项对应的可用枚举值用顿号'、'隔开），其余项需要你自己填写内容。
  请你进行推理并依次填写催记总结表单的11项要素，并只需要把整个表单内容包含在包裹在XML格式中输出：
  <res>依次填写的11项表单内容</res>
  有选项的务必严格进行选项选择，不要自由发挥。
    """
    qa_list = [
        {"question": "您好，这里是中国邮政储你好，这里是中国邮政储蓄银行。我的工号是086，请问是刘雷先生吗？嗯您好，请问是刘雷先生本人吗？对刘先生您好，您在我行办理的个人一手房贷款以及逾期截止到昨天逾期金额为1522.3元。请问您今天可以全额还款吗？先生。还了一天了，还了1300了。您是说除了这截止到昨天的1522.3元之外，您还还了1300了是吗？对，刚还了1300了。您什么时候还的呢？先生刚还了十来分钟。 好的，先生，那剩下的这一部分您什么时候还款呢？最近何时候可以还啊？先生，您说什么没有听清，您可以重复一下吗？最晚这这一笔后面那些最晚什么时候可以还啊？您是说最晚什么时候可以还是吗？先生，对，对啊。先生，是这样的，您的贷款呢目前已经处于逾期状态了 ，逾期会对您的真信产生影响，并产生罚息的。您在您没有逾期之前，您就应该还了。先生。现在还分了220多，那么最低可以什么时候还啊，现在还上哪去了。您是说您您是说您总共就欠了呃，您截止到昨天总共就欠了1522.3元，然后现在已经存了1300了，还差222.3元，是吗？啊，对，那现在先生您都已经存了这1300了。那现在差的这些都是小头，您看您能想想办法周转一下吗？尽快全额还款吗？行，好的，先生。因为您这部分款的话影响不大吧，您部分您部分还款是解除不了您的逾期状态的。先生嗯。您都大头都已经还了，就差这点小头，您尽快想想办法，尽快周转一下，然后尽快转让还款吧。嗯，，因为您就是差上1块钱呢，也是影响您的征信的呀，先生。😊你们的信用卡我有逾期吧件，你们是信与信用卡有关系吗？您是说您那边信用卡那，你你也办了我们银行的信用卡是吗？先生。对啊先生只要是逾期都会对征信产生影响的。我知道我征信现在已经花了应该是。那您能把这个还完的话，也对您的征信也会就不会造成进一步的影响啊。我知道就我 先还房贷，你那边信用卡的话，你们你这边出的信用卡吗？先生，这边的话只负责那个贷款提醒嗯。您如果说想要问信用卡这边的话，您可以联系一下您的客户经理。先生。嗯，你再说吧，那责任先还好金的。嗯，剩下的先生，那剩下的那200多块钱，那您什么时候还呢？尽快吧，那您今天能还上吗？先生嗯。尽请尽量吧，是吗？好的，先生，那你请您尽快周转，尽快确还款。好吧。哦，好的，先生，请问还有什么可以帮到您的吗？你这边借款率又高了又高了吗？哦，之前别是相机了。先生，针对于您询问的这个问题，您得详询一下您的客户经理， 您有客户经理的联系方式吗？有。那您联系一下客户经理，具体询问一下客户经理好吧。好的，好的，先生。那您这一次的话是什么原因造成的逾期呢？嗯，我这个这个房贷啊，是的，资金周转不过来。嗯，您是资金周转不过来，是工资没发吗？工资那边欠我这换了个货工资，当时那边欠我十来万没给我呢，还。能给我了，你慢慢的给我一下，我自己赚了一点。不的好，好的，先生，了解了。那如果没有其他问题的话，这边就先不打扰您了。再次提醒您呢尽快全额还款，以免对您的这些造成进一步影响，好吧。嗯，好，先生，感谢您的接听，再见。😊",
         "answer": """
         分析催收员和客户的对话，思考并推理一项项填写催记表单的11项内容。
        ...
        最终答案:
        <res>(所填写的11项表格内容)</res>
        """},
        {"question": "你好，这里是中国邮政储蓄银行，我的工号是068。请问您是卢鹏威先生吗？嗯对？😊呃，先生听不太清楚您那边说话，您是卢平伟先生本人是吧？是啊，怎么样了？怎么了？好，您在我行办理的个人一手房贷款已经逾期6天，截止到昨天，逾期金额为3345.61元。请问您今天可以全还款吗？😊不行，不得，没有钱的呢？嗯，您目前是什么原因还不了呢？是遇到什么困难了吗？呃，遇到困难了，没有工资，就是您的工资没有钱拿下来是吧？没有钱嗯嗯，您平常是几号发工资呢？没有工资发，现在失业了嗯，就是目前失业了是吧？那您现在有在找新的工作吗？我正在找没找到在哪里有这么好找工作啊。嗯，了解了，先生，嗯，也非常理解您的难处。因为是这样，就是看到您办的这笔房贷目前已经逾期6天了，逾期是会对您征信产生影响并产生罚息的。这边也是建议您嗯目前的话，如果说资金比较紧张，建议您先跟身边的亲戚朋友周转一下，先把您这个房贷全额还上。等之后您工作这边稳定了，也有正正常收入，再还给您亲戚朋友。这样一来也避免逾期时间。久了，对您征信造成进一步的影响。好的，我知道了。嗯，因为您办的这个毕竟是房贷嘛，逾期的话，对您征信产生影响之后，您再去办理别的业务，可能也是会受到影响。嗯，那您这边看周转一下，最快什么时间能够全额还上呢？10天之后，您是说在10天之后吗？嗯对。嗯，您这边的话10天之后是有其他的资金到账吗？还是说您去周转的话，要10天之后才能拿到资金呢？嗯，对。周转是吧嗯，先生这边的话，建议您就是抓紧时间呃，尽早的把这个房贷全额还上。因为您在等10天的话，到时候逾期时间就太久了。啊，那为什么呢？他怎么又会怎么样呢？嗯，您逾期时间久了，这边的话嗯也是会对您征信产生进一步影响的。所以咱们也是征信征信贴走到上，别走到征信有什么意义啊，现在连在吃饭都没有钱了，说什么征信啊。😊嗯，这边也能理解您的难处，但是您毕竟办的这个业务，当时也签署了合同约定的，建议您也是按照合同约定的时间来进行还款，你也出现逾期的情况。嗯，那这边的话就是有一个确切的还款时间吗？，那我不是跟你说合天之后吗？😊嗯 ，先生，那这边的话还是需要再次提示您一下，避免逾期时间久了，对您征信造成进一步影响，产生多东西。嗯，也建议您如果这个没有车，还可以这么征信的。嗯，您这边的话我不要了，这个所以我等对不要了哦，对不要了，我要这边的话就是您说这些气话的话，肯定也是解决不了这个事情，对不对？您现在的话也是建议那我都跟您想想，那我跟你说了，我都跟你说了，我都跟你周10天了，你还要在这里说叽唧歪歪都走这么多怎么用，那也是建议您尽早的全额还款，以免对您征心产生心理不，不了，找不了了其他问题，1天之。没有了十天之后找不了感谢你的接听再见。😊",
         "answer": ""},
        {"question":"您好，这里是中国邮政储蓄银行。我的工号是零八六。请问是史杰涵先生吗？是的是的。史先生您好，您在我行办理的优小贷贷款已经逾期，截止到昨天逾期。好晚晚24055，等下沈下会去搞啊啊，请问您是等下几点呢？😊嗯，七八点钟之前咯，因为我钱存现金还没都是现金，我都要存进去啊。嗯，了解了，那您只能七八点钟过去吗？不能早一点吗？有点事情搞完，我就下去过去啊，但是今天直接就搞掉啊。嗯，了解了，先生，是这样的，您的贷款呢目前已经逾期两天了。咱们扣款时间呢是在下午7点左右，所以说建议您呢在下午7点之前存款，避免扣款失败。因为如果扣款失败的话，会多逾期一天的，会产生相对应的罚息的，还会对您的征信产生相对应影响。好的。好好好，要的嗯，这边的话，建议您呢下午7点之前存款，好吧。嗯，好，谢谢啊，确定今天可以存进去是吧？嗯嗯嗯嗯。好，先生，那请问还有其他可以帮到您的吗？可有了。好，谢谢你啊。好啊，先生，不用客气，如果没有其他问题的话，这边就先不打扰您了，感谢您的配合，再见。😊",
         "answer": ""}
    ]

    # 启动第一轮优化
    modification_all, anaysis_all, new_prompt, new_answer, success = start_optimization(optimizer, current_prompt, qa_list)

    print(f"🚩 +++++++++返回前端接口结果+++++++++ 🚩")
    print("返回的大模型优化反思：", modification_all, "\n", anaysis_all)
    print("返回的当前优化后的prompt：", new_prompt)
    print("返回的当前优化后的问题执行结果：", new_answer)
    print("当前优化是否成功：", success)
    print("++++++++++++++++++++++++++++++++++++++")

    # 启动优化迭代
    while True:
        user_feedback = input("请用户根据上一轮的优化结果，输入你的优化建议（输入 'exit' 退出；没有建议则输入空字符串''）: ")
        if user_feedback.lower() == "exit":
            break

        modification_all, anaysis_all, new_prompt, new_answer, success = continue_optimization(
            optimizer, modification_all, anaysis_all, new_answer, new_prompt, qa_list)

        print(f"🚩 +++++++++返回前端接口结果+++++++++ 🚩\n")
        print("返回的大模型优化反思：", modification_all, "\n", anaysis_all)
        print("返回的当前优化后的prompt：", new_prompt)
        print("返回的当前优化后的问题执行结果：", new_answer)
        print("当前优化是否成功：", success)
        print("++++++++++++++++++++++++++++++++++++++")


