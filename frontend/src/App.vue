<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <h1>提示词优化系统</h1>
      </el-header>
      <el-main>
        <el-row :gutter="20">
          <!-- 左侧：初始数据 -->
          <el-col :span="12">
            <el-card class="box-card">
              <template #header>
                <div class="card-header">
                  <span>初始数据</span>
                </div>
              </template>
              <el-form :model="initialData" :rules="rules" ref="initialForm" label-position="top">
                <el-form-item label="初始提示词" prop="initial_prompt">
                  <el-tabs v-model="initialPromptActiveTab">
                    <el-tab-pane label="编辑" name="edit">
                      <el-input
                        type="textarea"
                        v-model="initialData.initial_prompt"
                        :rows="6"
                        placeholder="请输入初始提示词"
                      ></el-input>
                    </el-tab-pane>
                    <el-tab-pane label="预览" name="preview">
                      <div 
                        class="markdown-body"
                        v-html="renderMarkdown(initialData.initial_prompt)"
                      ></div>
                    </el-tab-pane>
                  </el-tabs>
                </el-form-item>
                <el-form-item label="初始成功经验">
                  <el-tabs v-model="initialExperienceActiveTab">
                    <el-tab-pane label="编辑" name="edit">
                      <el-input
                        type="textarea"
                        v-model="initialData.success_experience"
                        :rows="6"
                        placeholder="请输入初始成功经验（可选）"
                      ></el-input>
                    </el-tab-pane>
                    <el-tab-pane label="预览" name="preview">
                      <div 
                        class="markdown-body"
                        v-html="renderMarkdown(initialData.success_experience)"
                      ></div>
                    </el-tab-pane>
                  </el-tabs>
                </el-form-item>
                <el-form-item label="初始优化建议">
                  <el-tabs v-model="initialSuggestionActiveTab">
                    <el-tab-pane label="编辑" name="edit">
                      <el-input
                        type="textarea"
                        v-model="initialData.optimize_suggestion"
                        :rows="6"
                        placeholder="请输入初始优化建议（可选）"
                      ></el-input>
                    </el-tab-pane>
                    <el-tab-pane label="预览" name="preview">
                      <div 
                        class="markdown-body"
                        v-html="renderMarkdown(initialData.optimize_suggestion)"
                      ></div>
                    </el-tab-pane>
                  </el-tabs>
                </el-form-item>
                <el-form-item label="初始测试准确率">
                  <el-input-number
                    v-model="initialData.test_accuracy"
                    :precision="2"
                    :step="0.1"
                    :min="0"
                    :max="1"
                  ></el-input-number>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>

          <!-- 右侧：优化结果 -->
          <el-col :span="12">
            <el-card class="box-card">
              <template #header>
                <div class="card-header">
                  <span>优化结果</span>
                </div>
              </template>
              <el-form :model="optimizedData" label-position="top">
                <el-form-item label="优化后的提示词">
                  <el-tabs v-model="optimizedPromptActiveTab">
                    <el-tab-pane label="预览" name="preview">
                      <div 
                        class="markdown-body"
                        v-html="renderMarkdown(optimizedData.optimized_prompt)"
                      ></div>
                    </el-tab-pane>
                    <el-tab-pane label="源码" name="source">
                      <el-input
                        type="textarea"
                        v-model="optimizedData.optimized_prompt"
                        :rows="8"
                        readonly
                      ></el-input>
                    </el-tab-pane>
                  </el-tabs>
                </el-form-item>
                <el-form-item label="优化后的成功经验">
                  <el-tabs v-model="optimizedExperienceActiveTab">
                    <el-tab-pane label="预览" name="preview">
                      <div 
                        class="markdown-body"
                        v-html="renderMarkdown(optimizedData.success_experience)"
                      ></div>
                    </el-tab-pane>
                    <el-tab-pane label="源码" name="source">
                      <el-input
                        type="textarea"
                        v-model="optimizedData.success_experience"
                        :rows="6"
                        readonly
                      ></el-input>
                    </el-tab-pane>
                  </el-tabs>
                </el-form-item>
                <el-form-item label="优化后的优化建议">
                  <el-tabs v-model="optimizedSuggestionActiveTab">
                    <el-tab-pane label="预览" name="preview">
                      <div 
                        class="markdown-body"
                        v-html="renderMarkdown(optimizedData.optimize_suggestion)"
                      ></div>
                    </el-tab-pane>
                    <el-tab-pane label="源码" name="source">
                      <el-input
                        type="textarea"
                        v-model="optimizedData.optimize_suggestion"
                        :rows="6"
                      ></el-input>
                    </el-tab-pane>
                  </el-tabs>
                </el-form-item>
                <el-form-item label="优化后的测试准确率">
                  <el-input-number
                    v-model="optimizedData.test_accuracy"
                    :precision="2"
                    :step="0.1"
                    :min="0"
                    :max="1"
                    readonly
                  ></el-input-number>
                </el-form-item>
                <el-form-item label="执行时间">
                  <el-input v-model="optimizedData.execution_time" readonly></el-input>
                </el-form-item>
                <el-form-item label="消耗Token数">
                  <el-input v-model="optimizedData.total_tokens" readonly></el-input>
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>
        </el-row>

        <!-- 操作按钮 -->
        <el-row class="operation-row">
          <el-col :span="24" class="text-center">
            <el-button type="primary" @click="startOptimize" :loading="loading">
              开始优化
            </el-button>
          </el-col>
        </el-row>
      </el-main>
    </el-container>
  </div>
</template>

<script>
import axios from 'axios'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import 'github-markdown-css/github-markdown.css'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
})

export default {
  name: 'App',
  data() {
    return {
      loading: false,
      initialPromptActiveTab: 'edit',
      initialExperienceActiveTab: 'edit',
      initialSuggestionActiveTab: 'edit',
      optimizedPromptActiveTab: 'preview',
      optimizedExperienceActiveTab: 'preview',
      optimizedSuggestionActiveTab: 'preview',
      initialData: {
        initial_prompt: '',
        success_experience: '',
        optimize_suggestion: '',
        test_accuracy: null
      },
      optimizedData: {
        optimized_prompt: '',
        success_experience: '',
        optimize_suggestion: '',
        test_accuracy: null,
        execution_time: '',
        total_tokens: ''
      },
      rules: {
        initial_prompt: [
          { required: true, message: '请输入初始提示词', trigger: 'blur' }
        ]
      }
    }
  },
  methods: {
    renderMarkdown(text) {
      if (!text) return ''
      return md.render(text)
    },
    async startOptimize() {
      try {
        // 表单验证
        await this.$refs.initialForm.validate()
        
        // 如果已有优化结果，将其转移到初始数据
        if (this.optimizedData.optimized_prompt) {
          this.initialData = {
            initial_prompt: this.optimizedData.optimized_prompt,
            success_experience: this.optimizedData.success_experience,
            optimize_suggestion: this.optimizedData.optimize_suggestion,
            test_accuracy: this.optimizedData.test_accuracy
          }
          // 清空优化结果
          this.optimizedData = {
            optimized_prompt: '',
            success_experience: '',
            optimize_suggestion: '',
            test_accuracy: null,
            execution_time: '',
            total_tokens: ''
          }
        }

        this.loading = true
        const response = await api.post('/api/optimize', {
          initial_prompt: this.initialData.initial_prompt,
          success_experience: this.initialData.success_experience || null,
          optimize_suggestion: this.initialData.optimize_suggestion || null,
          test_accuracy: this.initialData.test_accuracy || null
        })

        // 更新优化结果
        this.optimizedData = {
          optimized_prompt: response.data.optimized_prompt,
          success_experience: response.data.success_experience,
          optimize_suggestion: response.data.optimize_suggestion,
          test_accuracy: response.data.test_accuracy,
          execution_time: response.data.execution_time,
          total_tokens: response.data.total_tokens
        }

        // 如果初始值为空，自动填充优化结果
        if (!this.initialData.success_experience) {
          this.initialData.success_experience = response.data.initial_success_experience
        }
        if (!this.initialData.optimize_suggestion) {
          this.initialData.optimize_suggestion = response.data.initial_optimize_suggestion
        }
        if (!this.initialData.test_accuracy) {
          this.initialData.test_accuracy = response.data.initial_test_accuracy
        }

        ElMessage.success('优化完成')
      } catch (error) {
        if (error.name === 'ValidationError') {
          ElMessage.error('请填写必要的信息')
        } else {
          ElMessage.error(error.response?.data?.detail || '优化失败，请重试')
        }
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style>
.app-container {
  padding: 20px;
}

.el-header {
  text-align: center;
  line-height: 60px;
  background-color: #f5f7fa;
}

.operation-row {
  margin-top: 20px;
}

.text-center {
  text-align: center;
}

.box-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.markdown-body {
  padding: 15px;
  background-color: #ffffff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  min-height: 120px;
  color: #000000 !important;
}

.el-tabs__content {
  padding: 15px 0;
}

/* 调整输入框和显示框的宽度 */
.el-form-item {
  width: 100%;
}

.el-tabs {
  width: 100%;
}

.el-textarea {
  width: 100%;
}

.el-textarea__inner {
  font-family: 'Courier New', Courier, monospace;
  width: 100% !important;
  min-height: 150px !important;
}

.el-tab-pane {
  width: 100%;
}

/* 调整表单布局 */
.el-form {
  width: 100%;
}

/* 调整标签的宽度和对齐方式 */
.el-form-item__label {
  text-align: left !important;
  padding-bottom: 8px;
  line-height: 20px;
  font-size: 14px;
  color: #606266;
}

/* 调整内容区域的宽度 */
.el-form-item__content {
  margin-left: 0 !important;
  width: 100% !important;
}

/* 调整表单项的布局方向 */
.el-form .el-form-item {
  flex-direction: column;
  align-items: flex-start;
}

/* 调整标签页内容的边距 */
.el-tabs__content {
  width: 95%;
  margin: 0 auto;
}

/* 确保预览区域也能完整显示 */
.markdown-body {
  width: 95%;
  box-sizing: border-box;
  margin: 0 auto;
  min-height: 150px !important;
}

/* 调整表单项的间距 */
.el-form-item {
  margin-bottom: 22px;
}

/* 调整数值输入框的宽度 */
.el-form-item.is-required .el-input-number,
.el-form-item .el-input-number {
  width: 180px;
}

/* 确保所有文本内容为黑色 */
.markdown-body * {
  color: #000000 !important;
}

/* 调整代码块的显示 */
.markdown-body pre,
.markdown-body code {
  background-color: #f6f8fa !important;
  border-radius: 3px;
  padding: 0.2em 0.4em;
}

.markdown-body pre code {
  padding: 1em;
  display: block;
}

/* 调整链接颜色 */
.markdown-body a {
  color: #0366d6 !important;
}

/* 调整表格样式 */
.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 1em 0;
  background-color: #ffffff;
}

.markdown-body table th,
.markdown-body table td {
  border: 1px solid #dfe2e5;
  padding: 8px 13px;
  background-color: #ffffff !important;
  color: #000000 !important;
}

.markdown-body table tr {
  background-color: #ffffff !important;
}

.markdown-body table tr:nth-child(2n) {
  background-color: #ffffff !important;
}

.markdown-body table thead tr {
  background-color: #ffffff !important;
}

.markdown-body table th {
  font-weight: 600;
  background-color: #ffffff !important;
}

/* 确保表格内的所有元素都使用黑色文字 */
.markdown-body table * {
  color: #000000 !important;
}
</style> 