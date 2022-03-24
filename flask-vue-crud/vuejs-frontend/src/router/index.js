import Vue from 'vue'
import Router from 'vue-router'
import AllSess from '@/components/all-sess'
import CreateSess from '@/components/create-sess'
import EditSess from '@/components/edit-sess'
import DeleteSess from '@/components/delete-sess'
import VerifyCode from '@/components/verifycode'
Vue.use(Router)
Vue.use(VueResource);

export default new Router({
  routes: [
    {
      path: '/',
      name: 'AllSess',
      component: AllSess
    },
    {
      path: '/create-sess',
      name: 'CreateSess',
      component: CreateSess
    },
    {
      path: '/verify-code',
      name: 'VerifyCode',
      component: VerifyCode
    },
    {
      path: '/edit-sess',
      name: 'EditSess',
      component: EditSess
    },
    {
      path: '/delete-sess',
      name: 'DeleteSess',
      component: DeleteSess
    }
  ]
})
