<template>
  <div class="app-container">
    <el-container>
      <el-header>
        <h1>提示词优化系统</h1>
        <div class="import-section">
          <input
            type="file"
            ref="fileInput"
            accept=".xlsx,.xls"
            style="display: none"
            @change="handleFileUpload"
          >
          <el-button type="primary" @click="triggerFileInput" :loading="importLoading">
            <i class="el-icon-upload"></i> 导入数据集
          </el-button>
          <span class="import-tip">支持 .xlsx 或 .xls 格式，需包含"用户输入"和"期望回复"两列</span>
        </div>
      </el-header>
      <el-main>
        <!-- 上方：初始数据和优化结果 -->
        <el-row :gutter="20">
          <!-- 左侧：初始数据 -->
          <el-col :span="12">
            <el-card class="box-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>初始数据</span>
                </div>
              </template>
              <div class="fixed-height-container">
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
                </el-form>
              </div>
            </el-card>
          </el-col>

          <!-- 右侧：优化结果 -->
          <el-col :span="12">
            <el-card class="box-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>优化结果</span>
                </div>
              </template>
              <div class="fixed-height-container">
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
                </el-form>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 执行信息和操作按钮 -->
        <el-row class="operation-row">
          <el-col :span="24">
            <el-card class="info-card" shadow="hover" v-if="optimizedData.execution_time || optimizedData.total_tokens">
              <el-row :gutter="20">
                <el-col :span="12">
                  <div class="info-item">
                    <label class="info-label">执行时间</label>
                    <el-input v-model="optimizedData.execution_time" readonly></el-input>
                  </div>
                </el-col>
                <el-col :span="12">
                  <div class="info-item">
                    <label class="info-label">消耗Token数</label>
                    <el-input v-model="optimizedData.total_tokens" readonly></el-input>
                  </div>
                </el-col>
              </el-row>
            </el-card>
          </el-col>
        </el-row>

        <!-- 模型参数设置 -->
        <el-row class="operation-row" :gutter="20">
          <!-- 优化模型参数 -->
          <el-col :span="12">
            <el-card class="model-param-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <i class="el-icon-s-tools card-icon"></i>
                  <span>优化模型参数</span>
                </div>
              </template>
              <div class="model-param-form">
                <div class="param-row single-row">
                  <div class="param-item full-width">
                    <label class="param-label">模型名称：</label>
                    <el-input v-model="optimizeModelParams.model_name" placeholder="请输入模型名称" class="param-input" style="font-size: 15px;">
                      <template #prefix><i class="el-icon-cpu"></i></template>
                    </el-input>
                  </div>
                </div>
                <div class="param-row single-row">
                  <div class="param-item full-width">
                    <label class="param-label">API密钥：</label>
                    <el-input v-model="optimizeModelParams.api_key" placeholder="请输入API密钥" show-password class="param-input" style="font-size: 15px;">
                      <template #prefix><i class="el-icon-key"></i></template>
                    </el-input>
                  </div>
                </div>
                <div class="param-row single-row">
                  <div class="param-item full-width">
                    <label class="param-label">接口地址：</label>
                    <el-input v-model="optimizeModelParams.base_url" placeholder="请输入接口地址" class="param-input" style="font-size: 15px;">
                      <template #prefix><i class="el-icon-link"></i></template>
                    </el-input>
                  </div>
                </div>
                <div class="param-row btn-row">
                  <div class="btn-container">
                    <el-button type="primary" @click="testConnection('optimize')" :loading="optimizeTestLoading" class="connect-btn" style="font-size: 15px;">
                      <i class="el-icon-connection"></i> 连接测试
                    </el-button>
                    <span v-if="optimizeConnected" class="connection-status success">
                      <i class="el-icon-success"></i> 已连接
                    </span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <!-- 测试模型参数 -->
          <el-col :span="12">
            <el-card class="model-param-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <i class="el-icon-s-data card-icon"></i>
                  <span>测试模型参数</span>
                </div>
              </template>
              <div class="model-param-form">
                <div class="param-row single-row">
                  <div class="param-item full-width">
                    <label class="param-label">模型名称：</label>
                    <el-input v-model="testModelParams.model_name" placeholder="请输入模型名称" class="param-input" style="font-size: 15px;">
                      <template #prefix><i class="el-icon-cpu"></i></template>
                    </el-input>
                  </div>
                </div>
                <div class="param-row single-row">
                  <div class="param-item full-width">
                    <label class="param-label">API密钥：</label>
                    <el-input v-model="testModelParams.api_key" placeholder="请输入API密钥" show-password class="param-input" style="font-size: 15px;">
                      <template #prefix><i class="el-icon-key"></i></template>
                    </el-input>
                  </div>
                </div>
                <div class="param-row single-row">
                  <div class="param-item full-width">
                    <label class="param-label">接口地址：</label>
                    <el-input v-model="testModelParams.base_url" placeholder="请输入接口地址" class="param-input" style="font-size: 15px;">
                      <template #prefix><i class="el-icon-link"></i></template>
                    </el-input>
                  </div>
                </div>
                <div class="param-row btn-row">
                  <div class="btn-container">
                    <el-button type="primary" @click="testConnection('test')" :loading="testTestLoading" class="connect-btn" style="font-size: 15px;">
                      <i class="el-icon-connection"></i> 连接测试
                    </el-button>
                    <span v-if="testConnected" class="connection-status success">
                      <i class="el-icon-success"></i> 已连接
                    </span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>

        <!-- 操作按钮 -->
        <el-row class="operation-row">
          <el-col :span="24" class="text-center">
            <div class="button-group">
              <el-button type="warning" @click="resetPrompt">提示词重置</el-button>
              <el-button type="primary" @click="startOptimize" :loading="loading">开始优化</el-button>
            </div>
          </el-col>
        </el-row>

        <!-- 下方：导入的数据集 -->
        <el-row v-if="importedData.length > 0">
          <el-col :span="24">
            <el-card class="box-card dataset-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <span>导入数据集</span>
                </div>
              </template>
              <el-table
                :data="importedData"
                border
                style="width: 100%"
                max-height="300"
              >
                <el-table-column
                  prop="input"
                  label="用户输入"
                  show-overflow-tooltip
                ></el-table-column>
                <el-table-column
                  prop="expected"
                  label="期望回复"
                  show-overflow-tooltip
                ></el-table-column>
                <el-table-column
                  label="初始提示词结果"
                  show-overflow-tooltip
                >
                  <template #default="scope">
                    <div class="result-cell">
                      <span v-if="scope.row.initialPromptResult">
                        <span v-if="normalizeString(scope.row.initialPromptResult) === normalizeString(scope.row.expected)" class="success-icon">✓</span>
                        <span v-else class="error-icon">✗</span>
                      </span>
                      <span>{{ scope.row.initialPromptResult }}</span>
                    </div>
                  </template>
                </el-table-column>
                <el-table-column
                  label="优化提示词结果"
                  show-overflow-tooltip
                >
                  <template #default="scope">
                    <div class="result-cell">
                      <span v-if="scope.row.optimizedPromptResult">
                        <span v-if="normalizeString(scope.row.optimizedPromptResult) === normalizeString(scope.row.expected)" class="success-icon">✓</span>
                        <span v-else class="error-icon">✗</span>
                      </span>
                      <span>{{ scope.row.optimizedPromptResult }}</span>
                    </div>
                  </template>
                </el-table-column>
              </el-table>
              
              <!-- 准确率显示框 -->
              <div class="accuracy-container" style="margin-top: 15px;">
                <el-row :gutter="20">
                  <el-col :span="12">
                    <div class="info-item accuracy-item">
                      <label class="info-label">初始准确率：</label>
                      <el-input 
                        v-model="initialAccuracyDisplay" 
                        readonly
                        placeholder="暂无初始准确率数据"
                        class="accuracy-input"
                      ></el-input>
                    </div>
                  </el-col>
                  <el-col :span="12">
                    <div class="info-item accuracy-item">
                      <label class="info-label">优化准确率：</label>
                      <el-input 
                        v-model="optimizedAccuracyDisplay" 
                        readonly
                        placeholder="暂无优化准确率数据"
                        class="accuracy-input"
                      ></el-input>
                    </div>
                  </el-col>
                </el-row>
              </div>
            </el-card>
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
import * as XLSX from 'xlsx'

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 300000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const api1 = axios.create({
  baseURL: 'http://localhost:8001',
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
      },
      importedData: [],
      importLoading: false,
      initialAccuracyDisplay: '',
      optimizedAccuracyDisplay: '',
      optimizeModelParams: {
        model_name: '',
        api_key: '',
        base_url: ''
      },
      testModelParams: {
        model_name: '',
        api_key: '',
        base_url: ''
      },
      optimizeTestLoading: false,
      testTestLoading: false,
      optimizeConnected: false,
      testConnected: false
    }
  },
  computed: {
    canStartOptimize() {
      return this.importedData.length > 0 && this.initialData.initial_prompt && this.optimizeConnected && this.testConnected;
    }
  },
  watch: {
    'optimizeModelParams.model_name': function() {
      this.optimizeConnected = false;
    },
    'optimizeModelParams.api_key': function() {
      this.optimizeConnected = false;
    },
    'optimizeModelParams.base_url': function() {
      this.optimizeConnected = false;
    },
    'testModelParams.model_name': function() {
      this.testConnected = false;
    },
    'testModelParams.api_key': function() {
      this.testConnected = false;
    },
    'testModelParams.base_url': function() {
      this.testConnected = false;
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
        
        // 校验各项条件
        const checkItems = []
        if (this.importedData.length === 0) {
          checkItems.push('请先导入数据集')
        }
        
        if (!this.optimizeConnected) {
          checkItems.push('请先完成优化模型连接测试')
        }
        
        if (!this.testConnected) {
          checkItems.push('请先完成测试模型连接测试')
        }
        
        if (checkItems.length > 0) {
          ElMessage.error(checkItems.join('，'))
          return
        }
        
        // 如果已有优化结果，将其转移到初始数据
        if (this.optimizedData.optimized_prompt) {
          // 转移提示词数据
          this.initialData = {
            initial_prompt: this.optimizedData.optimized_prompt,
            success_experience: this.optimizedData.success_experience,
            optimize_suggestion: this.optimizedData.optimize_suggestion,
            test_accuracy: this.optimizedData.test_accuracy
          }
          
          // 转移数据集结果
          if (this.importedData.length > 0) {
            this.importedData = this.importedData.map(item => ({
              ...item,
              initialPromptResult: item.optimizedPromptResult,
              optimizedPromptResult: ''
            }))
          }
          
          // 转移准确率显示
          this.initialAccuracyDisplay = this.optimizedAccuracyDisplay
          this.optimizedAccuracyDisplay = '暂无数据'
          
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
        const requestData = {
          initial_prompt: this.initialData.initial_prompt,
          success_experience: this.initialData.success_experience || null,
          optimize_suggestion: this.initialData.optimize_suggestion || null,
          test_accuracy: this.initialData.test_accuracy || null,
          test_dataset: this.importedData.length > 0 ? this.importedData : null,
          optimize_llm_config: {
            model_name: this.optimizeModelParams.model_name,
            api_key: this.optimizeModelParams.api_key,
            base_url: this.optimizeModelParams.base_url
          },
          test_llm_config: {
            model_name: this.testModelParams.model_name,
            api_key: this.testModelParams.api_key,
            base_url: this.testModelParams.base_url
          }
        }
        
        const response = await api.post('/discriminative/api/optimize', requestData)

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
        
        // 如果有测试结果数据，更新导入的数据集
        if (response.data.test_result && response.data.test_result.length > 0) {
          this.importedData = response.data.test_result
        }
        
        // 更新准确率显示
        this.initialAccuracyDisplay = this.calculateAccuracyDisplay('initial_test_accuracy')
        this.optimizedAccuracyDisplay = this.calculateAccuracyDisplay('test_accuracy')

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
    },
    triggerFileInput() {
      this.$refs.fileInput.click()
    },
    handleFileUpload(event) {
      const file = event.target.files[0]
      if (!file) return
      
      // 重置输入值，以便可以重复上传相同文件
      event.target.value = ''
      
      this.importLoading = true
      
      // 校验文件类型
      const validTypes = [
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      ]
      
      if (!validTypes.includes(file.type) && 
          !file.name.endsWith('.xlsx') && 
          !file.name.endsWith('.xls')) {
        ElMessage.error('请上传 Excel 文件（.xlsx 或 .xls）')
        this.importLoading = false
        return
      }
      
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target.result)
          const workbook = XLSX.read(data, { type: 'array' })
          const sheetName = workbook.SheetNames[0]
          const sheet = workbook.Sheets[sheetName]
          const jsonData = XLSX.utils.sheet_to_json(sheet)
          
          // 校验是否为空
          if (jsonData.length === 0) {
            ElMessage.error('文件内容为空')
            this.importLoading = false
            return
          }
          
          // 校验表头
          const headers = Object.keys(jsonData[0])
          if (!headers.includes('用户输入') || !headers.includes('期望回复')) {
            ElMessage.error('文件格式错误：缺少必要的表头（用户输入、期望回复）')
            this.importLoading = false
            return
          }
          
          // 过滤数据，只保留有效的行，并添加结果列
          this.importedData = jsonData
            .filter(row => row['用户输入'] && row['期望回复'])
            .map(row => ({
              input: row['用户输入'],
              expected: row['期望回复'],
              initialPromptResult: '',
              optimizedPromptResult: ''
            }))
          
          // 更新准确率显示框
          if (this.initialData.test_accuracy) {
            this.initialAccuracyDisplay = this.calculateAccuracyDisplay('initial_test_accuracy')
          } else {
            this.initialAccuracyDisplay = '暂无数据'
          }
          
          if (this.optimizedData.test_accuracy) {
            this.optimizedAccuracyDisplay = this.calculateAccuracyDisplay('test_accuracy')
          } else {
            this.optimizedAccuracyDisplay = '暂无数据'
          }
          
          ElMessage.success(`导入成功，共 ${this.importedData.length} 条数据`)
        } catch (error) {
          console.error(error)
          ElMessage.error('解析数据失败，请检查文件格式')
        } finally {
          this.importLoading = false
        }
      }
      
      reader.onerror = () => {
        ElMessage.error('文件读取失败')
        this.importLoading = false
      }
      
      reader.readAsArrayBuffer(file)
    },
    calculateAccuracyDisplay(field) {
      if (field === 'initial_test_accuracy') {
        if (this.initialData.test_accuracy === null || this.initialData.test_accuracy === undefined) {
          return '暂无数据'
        }
        return (this.initialData.test_accuracy * 100).toFixed(1) + '%'
      } else if (field === 'test_accuracy') {
        if (this.optimizedData.test_accuracy === null || this.optimizedData.test_accuracy === undefined) {
          return '暂无数据'
        }
        return (this.optimizedData.test_accuracy * 100).toFixed(1) + '%'
      }
      
      return '暂无数据'
    },
    resetPrompt() {
      // 保存初始提示词内容
      const initialPrompt = this.initialData.initial_prompt
      
      // 清空初始数据（除提示词外）
      this.initialData = {
        initial_prompt: initialPrompt,
        success_experience: '',
        optimize_suggestion: '',
        test_accuracy: null
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
      
      // 重置准确率显示
      this.initialAccuracyDisplay = '暂无数据'
      this.optimizedAccuracyDisplay = '暂无数据'
      
      // 如果有导入数据，清空结果
      if (this.importedData.length > 0) {
        this.importedData = this.importedData.map(item => ({
          ...item,
          initialPromptResult: '',
          optimizedPromptResult: ''
        }))
      }
      
      // 保持模型连接状态不变
      
      ElMessage.success('提示词已重置')
    },
    normalizeString(str) {
      if (typeof str !== 'string') str = String(str)
      return str.trim().toLowerCase().replace(/\s+/g, ' ')
    },
    async testConnection(type) {
      try {
        const params = type === 'optimize' ? this.optimizeModelParams : this.testModelParams
        
        // 验证参数不能为空
        if (!params.model_name || !params.api_key || !params.base_url) {
          ElMessage.error('请填写完整的模型参数信息')
          return
        }
        
        // 设置加载状态
        if (type === 'optimize') {
          this.optimizeTestLoading = true
        } else {
          this.testTestLoading = true
        }
        
        const response = await api1.post('/api/connect-test', {
          model_name: params.model_name,
          api_key: params.api_key,
          base_url: params.base_url
        })

        if (response.data.code === 200) {
          ElMessage.success('连接测试成功：' + response.data.msg)
          if (type === 'optimize') {
            this.optimizeConnected = true
          } else {
            this.testConnected = true
          }
        } else {
          ElMessage.error('连接测试失败：' + response.data.msg)
          if (type === 'optimize') {
            this.optimizeConnected = false
          } else {
            this.testConnected = false
          }
        }
      } catch (error) {
        ElMessage.error('连接测试失败：' + (error.response?.data?.msg || '请检查参数'))
        if (type === 'optimize') {
          this.optimizeConnected = false
        } else {
          this.testConnected = false
        }
      } finally {
        // 重置加载状态
        if (type === 'optimize') {
          this.optimizeTestLoading = false
        } else {
          this.testTestLoading = false
        }
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.import-section {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.import-tip {
  margin-top: 0.5rem;
  color: #909399;
  font-size: 0.8rem;
}

.operation-row {
  margin-top: 20px;
  margin-bottom: 20px;
}

.text-center {
  text-align: center;
}

.box-card {
  height: 100%;
  display: flex;
  flex-direction: column;
  margin-bottom: 20px;
}

.box-card .el-card__header {
  flex-shrink: 0;
}

.box-card .el-card__body {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 固定高度容器允许内容增长 */
.fixed-height-container {
  display: flex;
  flex-direction: column;
  flex-grow: 1;
  height: auto !important;
  overflow: visible !important;
  padding-right: 0 !important;
}

.fixed-height-container .el-form {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

/* 数据集卡片样式 */
.dataset-card {
  margin-top: 20px;
}

.markdown-body {
  padding: 15px;
  background-color: #ffffff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  flex-grow: 1;
  height: auto !important;
  min-height: 150px !important;
  overflow-y: auto !important;
  color: #000000 !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.el-tabs {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
}

.el-tabs__header {
  flex-shrink: 0;
  margin-bottom: 10px;
  padding: 0;
  order: -1; /* 确保标签页在顶部 */
}

.el-tabs__nav-wrap {
  display: flex;
  justify-content: flex-start;
}

.el-tabs__nav-wrap::after {
  height: 1px;
}

.el-tabs__active-bar {
  height: 2px;
}

.el-tabs__item {
  font-size: 14px;
  padding: 0 20px;
  height: 32px;
  line-height: 32px;
}

.el-tabs__content {
  flex-grow: 1;
  display: flex;
  padding: 0;
  overflow: visible !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.el-tab-pane {
  flex-grow: 1;
  display: flex;
  height: 100%;
  width: 100% !important;
  box-sizing: border-box !important;
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

/* 调整输入框和显示框的宽度 */
.el-form-item {
  margin-bottom: 25px;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.el-form-item:last-child {
  margin-bottom: 0;
}

/* 调整标签的宽度和对齐方式 */
.el-form-item__label {
  text-align: left !important;
  padding-bottom: 8px;
  line-height: 20px;
  font-size: 14px;
  color: #606266;
  flex-shrink: 0;
}

/* 表单布局 */
.el-form {
  width: 100%;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.el-form-item__content {
  margin-left: 0 !important;
  width: 100% !important;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.el-textarea {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.el-textarea__inner {
  flex-grow: 1;
  height: 150px !important;
  max-height: none !important;
  min-height: 0 !important;
}

.el-textarea {
  width: 100% !important;
}

.el-textarea__inner {
  height: 180px !important;
  max-height: 180px !important;
  min-height: 180px !important;
  overflow-y: auto !important;
  width: 100% !important;
  resize: none !important;
}

/* 调整数值输入框的宽度 */
.el-form-item.is-required .el-input-number,
.el-form-item .el-input-number {
  width: 180px;
}

/* 调整导入数据表格样式 */
.el-table {
  width: 100%;
  margin-bottom: 10px;
}

.el-table .cell {
  line-height: 1.5;
  padding: 8px;
  word-break: break-all;
}

.el-table th {
  background-color: #f5f7fa;
  color: #606266;
  font-weight: bold;
}

.el-table__row:hover {
  background-color: #f5f7fa;
}

.el-table__row td {
  border-bottom: 1px solid #ebeef5;
}

.table-tip {
  margin-top: 10px;
  color: #909399;
  font-size: 0.8rem;
}

/* 滚动条样式 */
.fixed-height-container::-webkit-scrollbar {
  width: 6px;
}

.fixed-height-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.fixed-height-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.fixed-height-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
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

.info-card {
  margin-bottom: 20px;
}

.info-card .el-form-item {
  margin-bottom: 0;
}

.info-card .el-card__body {
  padding: 15px;
}

.info-item {
  margin-bottom: 10px;
}

.info-label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

/* 准确率显示样式 */
.accuracy-item {
  display: flex;
  align-items: center;
}

.accuracy-item .info-label {
  display: inline-block;
  margin-bottom: 0;
  margin-right: 10px;
  white-space: nowrap;
}

.accuracy-input {
  width: 200px;
}

/* 结果单元格样式 */
.result-cell {
  display: flex;
  align-items: center;
}

.result-cell .status-icon {
  margin-right: 5px;
  display: inline-block;
  width: 16px;
}

.success-icon {
  color: #67C23A;
  font-size: 16px;
}

.error-icon {
  color: #F56C6C;
  font-size: 16px;
}

/* 按钮组样式 */
.button-group {
  display: flex;
  justify-content: center;
  gap: 20px;
}

/* 调整标签页样式，确保内容不会溢出 */
.el-tabs__content {
  overflow: visible;
}

/* 文本框和预览区域的固定高度和滚动条 */
.el-textarea__inner {
  height: 180px !important;
  max-height: 180px !important;
  min-height: 180px !important;
  overflow-y: auto !important;
}

.markdown-body {
  height: 180px !important;
  overflow-y: auto !important;
  margin-bottom: 15px !important;
  width: 100% !important;
}

/* 确保预览区域的边距和滚动条不影响布局 */
.el-tabs__content {
  overflow: visible !important;
  padding: 0 !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.el-tab-pane {
  width: 100% !important;
  box-sizing: border-box !important;
}

/* 调整表单项的布局方向 */
.el-form .el-form-item {
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 25px;
  flex: 1;
  display: flex;
}

/* 模型参数卡片样式 */
.model-param-card {
  margin-bottom: 20px;
  transition: all 0.3s;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.model-param-card:hover {
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.model-param-card .el-card__header {
  background-color: #f0f6ff;
  padding: 15px 20px;
  border-bottom: 1px solid #e6eef8;
}

.model-param-card .card-header {
  font-weight: bold;
  font-size: 16px;
  color: #1e66bd;
  display: flex;
  align-items: center;
}

.model-param-form {
  padding: 20px;
}

.param-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 15px;
}

.single-row {
  display: flex;
  margin-bottom: 15px;
}

.param-item {
  display: flex;
  align-items: center;
  width: 48%;
}

.full-width {
  width: 100%;
}

.param-label {
  font-weight: 600;
  color: #2c3e50;
  font-size: 15px;
  margin-right: 10px;
  white-space: nowrap;
  width: 90px;
  text-align: right;
}

.param-input {
  flex: 1;
}

.btn-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

.btn-container {
  display: flex;
  align-items: center;
}

.connect-btn {
  background: linear-gradient(135deg, #409EFF 0%, #007BFF 100%);
  border: none;
  padding: 10px 20px;
  font-weight: 600;
  border-radius: 6px;
  transition: all 0.3s;
  letter-spacing: 1px;
  width: 130px;
}

.connect-btn:hover {
  background: linear-gradient(135deg, #66b1ff 0%, #0d86ff 100%);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
  transform: translateY(-1px);
}

.connect-btn:active {
  transform: translateY(1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.2);
}

.connect-btn i {
  margin-right: 5px;
}

.card-icon {
  margin-right: 8px;
  font-size: 18px;
  color: #409EFF;
}

.connection-status {
  margin-left: 10px;
  font-size: 14px;
  display: flex;
  align-items: center;
}

.connection-status.success {
  color: #67C23A;
}

.connection-status i {
  margin-right: 5px;
}

.warning-icon {
  color: #E6A23C;
  font-size: 16px;
  margin-left: 5px;
  cursor: help;
}
</style> 