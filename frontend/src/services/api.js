import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

export const analyzeCreator = (handle, forceRefresh = false) =>
  api.post('/creator/analyze', { handle, force_refresh: forceRefresh })

export const getPipelineStatus = (handle) =>
  api.get(`/creator/${handle}/status`)

export const getCreator = (handle) =>
  api.get(`/creator/${handle}`)

export const getClassificationSummary = (handle) =>
  api.get(`/creator/${handle}/classification-summary`)

export const getPosts = (handle) =>
  api.get(`/creator/${handle}/posts`)

export const getPostComments = (handle, postId) =>
  api.get(`/creator/${handle}/posts/${postId}/comments`)

export const getAudience = (handle) =>
  api.get(`/creator/${handle}/audience`)

export default api
