<template>
  <AppLayout :userName="userName" title="Factoscope" @logout="handleLogout">
    <!-- Header -->
    <div class="header-row">
      <div>
        <p class="eyebrow">Cours</p>
        <h2>Titre du cours : {{ cours?.titre || (isLoadingCours ? 'Chargement...' : 'Cours') }}</h2>
        <p class="subtitle">Description du cours : {{ cours?.description || '' }}</p>
      </div>

      <div class="actions">
        <UiButton variant="ghost" @click="goBack">← Retour</UiButton>

        <UiButton variant="ghost" @click="refreshAll" :disabled="isBusy">
          {{ isBusy ? 'Chargement...' : 'Actualiser' }}
        </UiButton>

        <UiButton variant="primary" @click="showGamePicker = true">
          + Ajouter des jeux
        </UiButton>
      </div>
    </div>

    <!-- Alerts -->
    <div v-if="error" class="error-bar">
      <span>{{ error }}</span>
      <button class="close-x" @click="error = ''">×</button>
    </div>

    <div v-if="successMessage" class="success-bar">
      <span>{{ successMessage }}</span>
      <button class="close-x" @click="successMessage = ''">×</button>
    </div>

    <!-- Skeleton cours -->
    <div v-if="isLoadingCours && !cours" class="dashboard-grid">
      <div v-for="n in 2" :key="n" class="card skeleton">
        <div class="skeleton-line title"></div>
        <div class="skeleton-line"></div>
        <div class="skeleton-line short"></div>
      </div>
    </div>

    <!-- Pages -->
    <section class="panel">
      <div class="panel-head" style="cursor: default;">
        <div class="panel-title">
          <span class="icon">📄</span>
          <h3>Pages du cours</h3>
          <span v-if="pages.length" class="badge">{{ pages.length }}</span>
        </div>

        <UiButton variant="primary" @click="openAddModal" :disabled="isSaving || isLoadingPages">
          + Ajouter une page
        </UiButton>
      </div>

      <div class="panel-body">
        <div v-if="isLoadingPages" class="loading">
          <span class="spinner"></span>
          <span>Chargement des pages...</span>
        </div>

        <div v-else-if="pages.length === 0" class="empty">
          <p>Aucune page pour le moment.</p>
          <UiButton variant="primary" @click="openAddModal">Ajouter votre première page</UiButton>
        </div>

        <div v-else class="dashboard-grid">
          <div v-for="page in pages" :key="page.id" class="card">
            <template v-if="editingPageId === page.id">
              <h3>Modifier la page</h3>

              <textarea v-model="editingForm.description" class="textarea" rows="3"
                placeholder="Description"></textarea>

              <input v-model="editingForm.medias" class="input" placeholder="URLs médias séparées par des 'at' " />


              <div class="card-actions">
                <UiButton variant="ghost" @click="cancelEdit" :disabled="isSaving">Annuler</UiButton>
                <button class="danger" @click="deletePage(page.id)" :disabled="isSaving">Supprimer</button>
                <UiButton variant="primary" @click="savePage(page.id)" :disabled="isSaving">
                  {{ isSaving ? 'Enregistrement...' : 'Enregistrer' }}
                </UiButton>
              </div>
            </template>

            <template v-else>
              <div class="card-icon">📄</div>
              <h3>{{ (page.description || 'Aucune description').slice(0, 60) }}</h3>
              <p class="description">{{ page.description || '—' }}</p>
              <p class="meta" v-if="page.medias">Médias : {{ page.medias }}</p>

              <div class="card-actions">
                <UiButton variant="primary" @click="startEdit(page)">Éditer</UiButton>
              </div>
            </template>
          </div>
        </div>
      </div>
    </section>

    <!-- Jeux du cours -->
    <section class="panel">
      <div class="panel-head" style="cursor: default;">
        <div class="panel-title">
          <span class="icon">🎮</span>
          <h3>Jeux du cours</h3>
        </div>
      </div>

      <div class="panel-body">
        <div class="dashboard-grid">
          <!-- Texte à Trou -->
          <div class="card game-card" @click="openTATViewer">
            <div class="card-icon">✅</div>
            <h3>Texte à Trou</h3>
            <p class="description">{{ tatQuestions.length }} question(s)</p>
            <p class="meta">Clique pour voir (liste déroulante)</p>
          </div>

          <!-- QCM -->
          <div class="card game-card" @click="openQCMViewer">
            <div class="card-icon">📝</div>
            <h3>QCM</h3>
            <p class="description">{{ qcmQuestions.length }} question(s)</p>
            <p class="meta">Clique pour voir (liste déroulante)</p>
          </div>

          <!-- Jeu à Classement -->
          <div class="card game-card" @click="openClassementViewer">
            <div class="card-icon">🏆</div>
            <h3>Jeu à Classement</h3>
            <p class="description">{{ classementQuestions.length }} question(s)</p>
            <p class="meta">Clique pour voir (liste déroulante)</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Modal: Ajouter une page -->
    <div v-if="showAddModal" class="modal-backdrop" @click="closeAddModal">
      <div class="modal" @click.stop>
        <h3>Ajouter une page</h3>

        <label class="field">
          <span>Description</span>
          <textarea v-model="newPageForm.description" class="textarea" rows="3"
            placeholder="Décrivez le contenu de cette page"></textarea>
        </label>

        <label class="field">
          <span>Médias (URLs séparées par des "at")</span>
          <input v-model="newPageForm.medias" class="input" placeholder="https://.../image.jp@ https://.../video.mp4" />
        </label>

        <div class="card-actions" style="margin-top: 16px;">
          <UiButton variant="ghost" @click="closeAddModal" :disabled="isSaving">Annuler</UiButton>
          <UiButton variant="primary" @click="createPage" :disabled="isSaving || !newPageForm.description.trim()">
            {{ isSaving ? 'Création...' : 'Créer la page' }}
          </UiButton>
        </div>
      </div>
    </div>

    <!-- Modal: Choix jeu -->
    <div v-if="showGamePicker" class="modal-backdrop" @click="closeGamePicker">
      <div class="modal" @click.stop>
        <h3>Ajouter un jeu</h3>
        <p class="subtitle" style="margin-top:6px;">
          Choisis le type de jeu à ajouter au cours.
        </p>

        <div class="game-grid">
          <button class="game-tile" @click="chooseGame('qcm')">
            <div class="game-emoji">📝</div>
            <div class="game-title">QCM</div>
            <div class="game-desc">Questions à choix multiple</div>
          </button>

          <button class="game-tile" @click="chooseGame('tat')">
            <div class="game-emoji">✅</div>
            <div class="game-title">Texte à Trou</div>
            <div class="game-desc">4 réponses + bonne réponse</div>
          </button>

          <button class="game-tile" @click="chooseGame('classement')">
            <div class="game-emoji">🏆</div>
            <div class="game-title">Jeu à Classement</div>
            <div class="game-desc">Classer des éléments (texte/images)</div>
          </button>
        </div>

        <div class="card-actions" style="margin-top:16px;">
          <UiButton variant="ghost" @click="closeGamePicker">Fermer</UiButton>
        </div>
      </div>
    </div>

    <!-- Modal: Upload Texte à Trou -->
    <div v-if="showUploadTAT" class="modal-backdrop" @click="closeUploadTAT">
      <div class="modal" @click.stop>
        <h3>Importer Texte à Trou (CSV)</h3>
        <p class="subtitle" style="margin-top:6px;">
          Format : <code>texte;rep1;rep2;rep3;rep4;numero_bonne_reponse</code>
        </p>

        <div class="form-grid">
          <label class="field">
            <span>Fichier CSV</span>
            <input class="input" type="file" accept=".csv,text/csv" @change="onTATFileChange" />
          </label>
        </div>

        <div v-if="uploadError" class="error-bar" style="margin-top:10px;">
          {{ uploadError }}
        </div>

        <div class="card-actions" style="margin-top:16px;">
          <UiButton variant="ghost" @click="closeUploadTAT" :disabled="isUploadingTAT">Annuler</UiButton>
          <UiButton variant="primary" @click="submitTATUpload" :disabled="!tatFile || isUploadingTAT">
            {{ isUploadingTAT ? 'Import en cours...' : 'Importer' }}
          </UiButton>
        </div>
      </div>
    </div>


    <!-- Modal: Upload QCM -->
    <div v-if="showUploadQCM" class="modal-backdrop" @click="closeUploadQCM">
      <div class="modal" @click.stop>
        <h3>Importer QCM (CSV)</h3>
        <p class="subtitle" style="margin-top:6px;">
          Format : <code>question;rep1;rep2;rep3;rep4;solution</code>
        </p>

        <div class="form-grid">
          <label class="field">
            <span>Fichier CSV</span>
            <input class="input" type="file" accept=".csv,text/csv" @change="onQCMFileChange" />
          </label>
        </div>

        <div v-if="uploadError" class="error-bar" style="margin-top:10px;">
          {{ uploadError }}
        </div>

        <div class="card-actions" style="margin-top:16px;">
          <UiButton variant="ghost" @click="closeUploadQCM" :disabled="isUploadingQCM">Annuler</UiButton>
          <UiButton variant="primary" @click="submitQCMUpload" :disabled="!qcmFile || isUploadingQCM">
            {{ isUploadingQCM ? 'Import en cours...' : 'Importer' }}
          </UiButton>
        </div>
      </div>
    </div>

    <!-- Modal: Upload Jeu à Classement -->
    <div v-if="showUploadClassement" class="modal-backdrop" @click="closeUploadClassement">
      <div class="modal" @click.stop>
        <h3>Importer Jeu à Classement (CSV)</h3>
        <p class="subtitle" style="margin-top:6px;">
          Format : <code>question;element1;element2;element3;element4;ordre_solution;type_elements</code>
        </p>
        <p class="subtitle" style="margin-top:4px; font-size:12px; color:#666;">
          Exemple ordre: <code>2&lt;1&lt;4&lt;3</code> | Type: <code>texte</code> ou <code>images</code>
        </p>

        <div class="form-grid">
          <label class="field">
            <span>Fichier CSV</span>
            <input class="input" type="file" accept=".csv,text/csv" @change="onClassementFileChange" />
          </label>
        </div>

        <div v-if="uploadError" class="error-bar" style="margin-top:10px;">
          {{ uploadError }}
        </div>

        <div class="card-actions" style="margin-top:16px;">
          <UiButton variant="ghost" @click="closeUploadClassement" :disabled="isUploadingClassement">Annuler</UiButton>
          <UiButton variant="primary" @click="submitClassementUpload"
            :disabled="!classementFile || isUploadingClassement">
            {{ isUploadingClassement ? 'Import en cours...' : 'Importer' }}
          </UiButton>
        </div>
      </div>
    </div>

    <!-- Modal: Viewer Text à True (accordion) -->
    <div v-if="showTATViewer" class="modal-backdrop" @click="closeTATViewer">
      <div class="modal modal-big" @click.stop>
        <div class="modal-top">
          <div>
            <h3 style="margin:0;">Texte à Trou — Questions</h3>
            <p class="subtitle" style="margin:6px 0 0;">
              Clique sur une question pour dérouler les réponses.
            </p>
          </div>

          <div class="modal-top-actions">
            <UiButton variant="ghost" @click="showUploadTAT = true">Importer CSV</UiButton>
            <button class="close-x" @click="closeTATViewer">×</button>
          </div>
        </div>

        <div v-if="isLoadingTAT" class="loading" style="margin-top:12px;">
          <span class="spinner"></span> Chargement...
        </div>

        <div v-else-if="tatQuestions.length === 0" class="empty" style="margin-top:12px;">
          <p>Aucune question importée pour ce cours.</p>
          <UiButton variant="primary" @click="showUploadTAT = true">Importer CSV</UiButton>
        </div>

        <div v-else class="tat-accordion" style="margin-top:12px;">
          <div v-for="(q, i) in tatQuestions" :key="q.id" class="acc-item" :class="{ open: openTATId === q.id }">
            <!-- Header -->
            <button class="acc-head" @click="toggleTAT(q.id)">
              <div class="acc-left">
                <span class="acc-index">#{{ i + 1 }}</span>
                <span class="acc-text">{{ q.texte }}</span>
              </div>

              <div class="acc-right">
                <span class="pill">Bonne : {{ q.numero_reponse_correcte }}</span>
                <span class="chev">{{ openTATId === q.id ? '▾' : '▸' }}</span>
              </div>
            </button>

            <!-- Body -->
            <div v-if="openTATId === q.id" class="acc-body">

              <!-- MODE EDIT -->
              <div v-if="editingTATId === q.id" class="edit-box">
                <label>Question</label>
                <textarea v-model="tatEditForm.texte" class="textarea" rows="2"></textarea>

                <label>Réponse 1</label>
                <input v-model="tatEditForm.reponse1" class="input" />

                <label>Réponse 2</label>
                <input v-model="tatEditForm.reponse2" class="input" />

                <label>Réponse 3</label>
                <input v-model="tatEditForm.reponse3" class="input" />

                <label>Réponse 4</label>
                <input v-model="tatEditForm.reponse4" class="input" />

                <label>Bonne réponse (1-4)</label>
                <input type="number" min="1" max="4" v-model.number="tatEditForm.numero_reponse_correcte"
                  class="input" />

                <label>Explication</label>
                <textarea v-model="tatEditForm.explication" class="textarea" rows="2"></textarea>

                <div class="card-actions">
                  <UiButton variant="ghost" @click="cancelEditTAT">Annuler</UiButton>
                  <UiButton variant="primary" @click="saveEditTAT(q.id)">Enregistrer</UiButton>
                </div>
              </div>

              <!-- MODE VIEW -->
              <div v-else>
                <div class="answers">
                  <div class="answer" :class="{ correct: q.numero_reponse_correcte === 1 }">
                    <span class="answer-letter">1)</span>
                    <span>{{ q.reponse1 }}</span>
                  </div>
                  <div class="answer" :class="{ correct: q.numero_reponse_correcte === 2 }">
                    <span class="answer-letter">2)</span>
                    <span>{{ q.reponse2 }}</span>
                  </div>
                  <div class="answer" :class="{ correct: q.numero_reponse_correcte === 3 }">
                    <span class="answer-letter">3)</span>
                    <span>{{ q.reponse3 }}</span>
                  </div>
                  <div class="answer" :class="{ correct: q.numero_reponse_correcte === 4 }">
                    <span class="answer-letter">4)</span>
                    <span>{{ q.reponse4 }}</span>
                  </div>
                </div>

                <p v-if="q.explication" class="explain">
                  <strong>Explication :</strong> {{ q.explication }}
                </p>

                <div class="acc-actions">
                  <UiButton variant="ghost" @click="startEditTAT(q)">✏️ Modifier</UiButton>
                  <button class="danger" @click="deleteTAT(q.id)">Supprimer</button>
                </div>
              </div>
            </div>

          </div>
        </div>

        <div class="modal-footer-lite">
          <UiButton variant="ghost" @click="closeTATViewer">Fermer</UiButton>
        </div>
      </div>
    </div>

    <!-- Modal: Viewer QCM (accordion) -->
    <div v-if="showQCMViewer" class="modal-backdrop" @click="closeQCMViewer">
      <div class="modal modal-big" @click.stop>
        <div class="modal-top">
          <div>
            <h3 style="margin:0;">QCM — Questions</h3>
            <p class="subtitle" style="margin:6px 0 0;">
              Clique sur une question pour dérouler les réponses.
            </p>
          </div>

          <div class="modal-top-actions">
            <UiButton variant="ghost" @click="showUploadQCM = true">Importer CSV</UiButton>
            <button class="close-x" @click="closeQCMViewer">×</button>
          </div>
        </div>

        <div v-if="isLoadingQCM" class="loading" style="margin-top:12px;">
          <span class="spinner"></span> Chargement...
        </div>

        <div v-else-if="qcmQuestions.length === 0" class="empty" style="margin-top:12px;">
          <p>Aucune question QCM importée pour ce cours.</p>
          <UiButton variant="primary" @click="showUploadQCM = true">Importer CSV</UiButton>
        </div>

        <div v-else class="qcm-accordion" style="margin-top:12px;">
          <div v-for="(q, i) in qcmQuestions" :key="q.id" class="acc-item" :class="{ open: openQCMId === q.id }">
            <!-- Header -->
            <button class="acc-head" @click="toggleQCM(q.id)">
              <div class="acc-left">
                <span class="acc-index">#{{ i + 1 }}</span>
                <span class="acc-text">{{ q.question }}</span>
              </div>

              <div class="acc-right">
                <span class="pill">Solution : {{ q.soluce }}</span>
                <span class="chev">{{ openQCMId === q.id ? '▾' : '▸' }}</span>
              </div>
            </button>

            <!-- Body -->
            <div v-if="openQCMId === q.id" class="acc-body">
              <!-- MODE EDIT -->
              <div v-if="editingQCMId === q.id" class="edit-box">
                <label>Question</label>
                <textarea v-model="qcmEditForm.question" class="textarea" rows="2"></textarea>

                <label>Réponse 1</label>
                <input v-model="qcmEditForm.rep1" class="input" />

                <label>Réponse 2</label>
                <input v-model="qcmEditForm.rep2" class="input" />

                <label>Réponse 3</label>
                <input v-model="qcmEditForm.rep3" class="input" />

                <label>Réponse 4</label>
                <input v-model="qcmEditForm.rep4" class="input" />

                <label>Solution (1-4)</label>
                <input type="number" min="1" max="4" v-model.number="qcmEditForm.soluce" class="input" />

                <div class="card-actions">
                  <UiButton variant="ghost" @click="cancelEditQCM">Annuler</UiButton>
                  <UiButton variant="primary" @click="saveEditQCM(q.id)">Enregistrer</UiButton>
                </div>
              </div>

              <!-- MODE VIEW -->
              <div v-else>
                <div class="answers">
                  <div class="answer" :class="{ correct: q.soluce === 1 }">
                    <span class="answer-letter">1)</span>
                    <span>{{ q.rep1 }}</span>
                  </div>
                  <div class="answer" :class="{ correct: q.soluce === 2 }">
                    <span class="answer-letter">2)</span>
                    <span>{{ q.rep2 }}</span>
                  </div>
                  <div class="answer" :class="{ correct: q.soluce === 3 }">
                    <span class="answer-letter">3)</span>
                    <span>{{ q.rep3 }}</span>
                  </div>
                  <div class="answer" :class="{ correct: q.soluce === 4 }">
                    <span class="answer-letter">4)</span>
                    <span>{{ q.rep4 }}</span>
                  </div>
                </div>

                <div class="acc-actions">
                  <UiButton variant="ghost" @click="startEditQCM(q)">✏️ Modifier</UiButton>
                  <button class="danger" @click="deleteQCM(q.id)">Supprimer</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer-lite">
          <UiButton variant="ghost" @click="closeQCMViewer">Fermer</UiButton>
        </div>
      </div>
    </div>

    <!-- Modal: Viewer Jeu à Classement (accordion) -->
    <div v-if="showClassementViewer" class="modal-backdrop" @click="closeClassementViewer">
      <div class="modal modal-big" @click.stop>
        <div class="modal-top">
          <div>
            <h3 style="margin:0;">Jeu à Classement — Questions</h3>
            <p class="subtitle" style="margin:6px 0 0;">
              Clique sur une question pour dérouler les éléments à classer.
            </p>
          </div>

          <div class="modal-top-actions">
            <UiButton variant="ghost" @click="showUploadClassement = true">Importer CSV</UiButton>
            <button class="close-x" @click="closeClassementViewer">×</button>
          </div>
        </div>

        <div v-if="isLoadingClassement" class="loading" style="margin-top:12px;">
          <span class="spinner"></span> Chargement...
        </div>

        <div v-else-if="classementQuestions.length === 0" class="empty" style="margin-top:12px;">
          <p>Aucune question de classement importée pour ce cours.</p>
          <UiButton variant="primary" @click="showUploadClassement = true">Importer CSV</UiButton>
        </div>

        <div v-else class="classement-accordion" style="margin-top:12px;">
          <div v-for="(q, i) in classementQuestions" :key="q.id" class="acc-item"
            :class="{ open: openClassementId === q.id }">
            <!-- Header -->
            <button class="acc-head" @click="toggleClassement(q.id)">
              <div class="acc-left">
                <span class="acc-index">#{{ i + 1 }}</span>
                <span class="acc-text">{{ q.question }}</span>
              </div>

              <div class="acc-right">
                <span class="pill">{{ q.type_elements }}</span>
                <span class="chev">{{ openClassementId === q.id ? '▾' : '▸' }}</span>
              </div>
            </button>

            <!-- Body -->
            <div v-if="openClassementId === q.id" class="acc-body">
              <!-- MODE EDIT -->
              <div v-if="editingClassementId === q.id" class="edit-box">
                <label>Question</label>
                <textarea v-model="classementEditForm.question" class="textarea" rows="2"></textarea>

                <label>Élément 1</label>
                <input v-model="classementEditForm.element1" class="input" />

                <label>Élément 2</label>
                <input v-model="classementEditForm.element2" class="input" />

                <label>Élément 3</label>
                <input v-model="classementEditForm.element3" class="input" />

                <label>Élément 4</label>
                <input v-model="classementEditForm.element4" class="input" />

                <label>Ordre solution (ex: 2&lt;1&lt;4&lt;3)</label>
                <input v-model="classementEditForm.ordre_solution" class="input" />

                <label>Type d'éléments</label>
                <select v-model="classementEditForm.type_elements" class="input">
                  <option value="texte">Texte</option>
                  <option value="images">Images</option>
                </select>

                <div class="card-actions">
                  <UiButton variant="ghost" @click="cancelEditClassement">Annuler</UiButton>
                  <UiButton variant="primary" @click="saveEditClassement(q.id)">Enregistrer</UiButton>
                </div>
              </div>

              <!-- MODE VIEW -->
              <div v-else>
                <div class="elements">
                  <div class="element">
                    <span class="element-number">1)</span>
                    <span v-if="q.type_elements === 'images'">
                      <img :src="q.element1" alt="Élément 1"
                        style="max-width:100px; max-height:100px; object-fit:cover; border-radius:8px;" />
                    </span>
                    <span v-else>{{ q.element1 }}</span>
                  </div>
                  <div class="element">
                    <span class="element-number">2)</span>
                    <span v-if="q.type_elements === 'images'">
                      <img :src="q.element2" alt="Élément 2"
                        style="max-width:100px; max-height:100px; object-fit:cover; border-radius:8px;" />
                    </span>
                    <span v-else>{{ q.element2 }}</span>
                  </div>
                  <div class="element">
                    <span class="element-number">3)</span>
                    <span v-if="q.type_elements === 'images'">
                      <img :src="q.element3" alt="Élément 3"
                        style="max-width:100px; max-height:100px; object-fit:cover; border-radius:8px;" />
                    </span>
                    <span v-else>{{ q.element3 }}</span>
                  </div>
                  <div class="element">
                    <span class="element-number">4)</span>
                    <span v-if="q.type_elements === 'images'">
                      <img :src="q.element4" alt="Élément 4"
                        style="max-width:100px; max-height:100px; object-fit:cover; border-radius:8px;" />
                    </span>
                    <span v-else>{{ q.element4 }}</span>
                  </div>
                </div>

                <div class="solution-info"
                  style="margin-top:12px; padding:8px; background:#f0f4ff; border-radius:8px; font-size:14px;">
                  <strong>Ordre solution :</strong> {{ q.ordre_solution }}
                </div>

                <div class="acc-actions">
                  <UiButton variant="ghost" @click="startEditClassement(q)">✏️ Modifier</UiButton>
                  <button class="danger" @click="deleteClassement(q.id)">Supprimer</button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer-lite">
          <UiButton variant="ghost" @click="closeClassementViewer">Fermer</UiButton>
        </div>
      </div>
    </div>
  </AppLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import UiButton from '@/components/UiButton.vue'

const router = useRouter()
const route = useRoute()
const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const userName = ref(localStorage.getItem('userName') || 'Utilisateur')

const cours = ref(null)
const pages = ref([])
const error = ref('')
const successMessage = ref('')

const isLoadingCours = ref(false)
const isLoadingPages = ref(false)
const isSaving = ref(false)

const coursId = computed(() => Number(route.params.id))
const isBusy = computed(() => isLoadingCours.value || isLoadingPages.value)

// ---------- Jeux ----------
const showGamePicker = ref(false)
const showUploadTAT = ref(false)
const showUploadQCM = ref(false)
const showUploadClassement = ref(false)
const uploadError = ref('')
const tatFile = ref(null)
const qcmFile = ref(null)
const classementFile = ref(null)
const isUploadingTAT = ref(false)
const isUploadingQCM = ref(false)
const isUploadingClassement = ref(false)

const showTATViewer = ref(false)
const showQCMViewer = ref(false)
const showClassementViewer = ref(false)
const isLoadingTAT = ref(false)
const isLoadingQCM = ref(false)
const isLoadingClassement = ref(false)
const tatQuestions = ref([])
const qcmQuestions = ref([])
const classementQuestions = ref([])

// accordion state
const openTATId = ref(null)
const openQCMId = ref(null)
const openClassementId = ref(null)

// ---------- Pages forms ----------
const showAddModal = ref(false)
const newPageForm = ref({ description: '', medias: '' })
const editingPageId = ref(null)
const editingForm = ref({ description: '', medias: '' })
const editingTATId = ref(null)
const tatEditForm = ref({
  texte: '',
  reponse1: '',
  reponse2: '',
  reponse3: '',
  reponse4: '',
  numero_reponse_correcte: 1,
  explication: ''
})
const editingQCMId = ref(null)
const qcmEditForm = ref({
  question: '',
  rep1: '',
  rep2: '',
  rep3: '',
  rep4: '',
  soluce: 1
})
const editingClassementId = ref(null)
const classementEditForm = ref({
  question: '',
  element1: '',
  element2: '',
  element3: '',
  element4: '',
  ordre_solution: '',
  type_elements: 'texte'
})
const startEditTAT = (q) => {
  editingTATId.value = q.id
  tatEditForm.value = {
    texte: q.texte,
    reponse1: q.reponse1,
    reponse2: q.reponse2,
    reponse3: q.reponse3,
    reponse4: q.reponse4,
    numero_reponse_correcte: q.numero_reponse_correcte,
    explication: q.explication || ''
  }
  openTATId.value = q.id
}

const cancelEditTAT = () => {
  editingTATId.value = null
}

const saveEditTAT = async (id) => {
  try {
    await apiFetch(`${apiBase}/api/text-a-true/${id}`, {
      method: 'PUT',
      body: JSON.stringify(tatEditForm.value)
    })

    successMessage.value = "Question mise à jour"
    editingTATId.value = null
    await fetchTAT()

  } catch (e) {
    error.value = e.message || "Erreur modification question"
  }
}

const startEditQCM = (q) => {
  editingQCMId.value = q.id
  qcmEditForm.value = {
    question: q.question,
    rep1: q.rep1,
    rep2: q.rep2,
    rep3: q.rep3,
    rep4: q.rep4,
    soluce: q.soluce
  }
  openQCMId.value = q.id
}

const cancelEditQCM = () => {
  editingQCMId.value = null
}

const saveEditQCM = async (id) => {
  try {
    await apiFetch(`${apiBase}/api/qcm/${id}`, {
      method: 'PUT',
      body: JSON.stringify(qcmEditForm.value)
    })

    successMessage.value = "Question QCM mise à jour"
    editingQCMId.value = null
    await fetchQCM()

  } catch (e) {
    error.value = e.message || "Erreur modification question QCM"
  }
}

const startEditClassement = (q) => {
  editingClassementId.value = q.id
  classementEditForm.value = {
    question: q.question,
    element1: q.element1,
    element2: q.element2,
    element3: q.element3,
    element4: q.element4,
    ordre_solution: q.ordre_solution,
    type_elements: q.type_elements
  }
  openClassementId.value = q.id
}

const cancelEditClassement = () => {
  editingClassementId.value = null
}

const saveEditClassement = async (id) => {
  try {
    await apiFetch(`${apiBase}/api/jeu-classement/${id}`, {
      method: 'PUT',
      body: JSON.stringify(classementEditForm.value)
    })

    successMessage.value = "Question de classement mise à jour"
    editingClassementId.value = null
    await fetchClassement()

  } catch (e) {
    error.value = e.message || "Erreur modification question de classement"
  }
}

// ---------- Helpers ----------
const getTokenOrRedirect = () => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return null
  }
  return token
}

const apiFetch = async (url, options = {}) => {
  const token = getTokenOrRedirect()
  if (!token) throw new Error('Non authentifié')

  const headers = options.headers ? { ...options.headers } : {}
  headers.Authorization = `Bearer ${token}`

  const isForm = options.body instanceof FormData
  if (!isForm && options.method && options.method !== 'GET') {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json'
  }

  const res = await fetch(url, { ...options, headers })
  if (!res.ok) {
    const msg = await res.json().catch(() => ({}))
    throw new Error(msg.detail || msg.message || 'Erreur API')
  }
  if (res.status === 204) return null
  return res.json().catch(() => ({}))
}

// ---------- API calls ----------
const fetchCours = async () => {
  if (!coursId.value) return
  isLoadingCours.value = true
  error.value = ''
  try {
    cours.value = await apiFetch(`${apiBase}/api/cours/${coursId.value}`, { method: 'GET' })
  } catch (e) {
    error.value = e.message || 'Erreur chargement cours'
  } finally {
    isLoadingCours.value = false
  }
}

const fetchPages = async () => {
  if (!coursId.value) return
  isLoadingPages.value = true
  error.value = ''
  try {
    const allPages = await apiFetch(`${apiBase}/api/pages`, { method: 'GET' })
    pages.value = Array.isArray(allPages) ? allPages.filter(p => p.id_cours === coursId.value) : []
  } catch (e) {
    error.value = e.message || 'Erreur chargement pages'
  } finally {
    isLoadingPages.value = false
  }
}

const fetchTAT = async () => {
  if (!coursId.value) return
  isLoadingTAT.value = true
  error.value = ''
  try {
    const data = await apiFetch(`${apiBase}/api/text-a-true/${coursId.value}`, { method: 'GET' })
    tatQuestions.value = Array.isArray(data) ? data : []
    // ouvrir automatiquement la première question si existe
    openTATId.value = tatQuestions.value[0]?.id ?? null
  } catch (e) {
    error.value = e.message || 'Erreur chargement Texte à Trou'
    tatQuestions.value = []
    openTATId.value = null
  } finally {
    isLoadingTAT.value = false
  }
}

const fetchQCM = async () => {
  if (!coursId.value) return
  isLoadingQCM.value = true
  error.value = ''
  try {
    const data = await apiFetch(`${apiBase}/api/qcm/${coursId.value}`, { method: 'GET' })
    qcmQuestions.value = Array.isArray(data) ? data : []
    // ouvrir automatiquement la première question si existe
    openQCMId.value = qcmQuestions.value[0]?.id ?? null
  } catch (e) {
    error.value = e.message || 'Erreur chargement QCM'
    qcmQuestions.value = []
    openQCMId.value = null
  } finally {
    isLoadingQCM.value = false
  }
}

const fetchClassement = async () => {
  if (!coursId.value) return
  isLoadingClassement.value = true
  error.value = ''
  try {
    const data = await apiFetch(`${apiBase}/api/jeu-classement/${coursId.value}`, { method: 'GET' })
    classementQuestions.value = Array.isArray(data) ? data : []
    // ouvrir automatiquement la première question si existe
    openClassementId.value = classementQuestions.value[0]?.id ?? null
  } catch (e) {
    error.value = e.message || 'Erreur chargement Jeu à Classement'
    classementQuestions.value = []
    openClassementId.value = null
  } finally {
    isLoadingClassement.value = false
  }
}

// ---------- Pages actions ----------
const openAddModal = () => {
  newPageForm.value = { description: '', medias: '' }
  showAddModal.value = true
}
const closeAddModal = () => (showAddModal.value = false)

const createPage = async () => {
  if (!newPageForm.value.description.trim()) return
  isSaving.value = true
  error.value = ''
  successMessage.value = ''
  try {
    await apiFetch(`${apiBase}/api/pages/`, {
      method: 'POST',
      body: JSON.stringify({
        id_cours: coursId.value,
        description: newPageForm.value.description,
        medias: newPageForm.value.medias
      })
    })
    closeAddModal()
    await fetchPages()
    successMessage.value = 'Page créée'
  } catch (e) {
    error.value = e.message || 'Erreur création page'
  } finally {
    isSaving.value = false
  }
}

const startEdit = (page) => {
  editingPageId.value = page.id
  editingForm.value = { description: page.description || '', medias: page.medias || '' }
}
const cancelEdit = () => (editingPageId.value = null)

const savePage = async (pageId) => {
  if (!editingForm.value.description.trim()) {
    error.value = 'La description est requise'
    return
  }
  isSaving.value = true
  error.value = ''
  successMessage.value = ''
  try {
    await apiFetch(`${apiBase}/api/pages/${pageId}`, {
      method: 'PUT',
      body: JSON.stringify(editingForm.value)
    })
    editingPageId.value = null
    await fetchPages()
    successMessage.value = 'Page mise à jour'
  } catch (e) {
    error.value = e.message || 'Erreur update page'
  } finally {
    isSaving.value = false
  }
}

const deletePage = async (pageId) => {
  if (!confirm('Supprimer cette page ?')) return
  isSaving.value = true
  error.value = ''
  successMessage.value = ''
  try {
    await apiFetch(`${apiBase}/api/pages/${pageId}`, { method: 'DELETE' })
    pages.value = pages.value.filter(p => p.id !== pageId)
    editingPageId.value = null
    successMessage.value = 'Page supprimée'
  } catch (e) {
    error.value = e.message || 'Erreur suppression page'
  } finally {
    isSaving.value = false
  }
}

// ---------- Jeux actions ----------
const closeGamePicker = () => (showGamePicker.value = false)

const chooseGame = (type) => {
  showGamePicker.value = false
  if (type === 'tat') showUploadTAT.value = true
  if (type === 'qcm') showUploadQCM.value = true
  if (type === 'classement') showUploadClassement.value = true
}

const closeUploadTAT = () => {
  showUploadTAT.value = false
  uploadError.value = ''
  tatFile.value = null
}

const closeUploadQCM = () => {
  showUploadQCM.value = false
  uploadError.value = ''
  qcmFile.value = null
}

const closeUploadClassement = () => {
  showUploadClassement.value = false
  uploadError.value = ''
  classementFile.value = null
}

const onTATFileChange = (e) => {
  tatFile.value = e.target.files?.[0] || null
}

const onQCMFileChange = (e) => {
  qcmFile.value = e.target.files?.[0] || null
}

const onClassementFileChange = (e) => {
  classementFile.value = e.target.files?.[0] || null
}

const submitTATUpload = async () => {
  if (!tatFile.value) return
  isUploadingTAT.value = true
  uploadError.value = ''
  error.value = ''
  successMessage.value = ''

  if (!tatFile.value.name.toLowerCase().endsWith('.csv')) {
    uploadError.value = 'Le fichier doit être .csv'
    isUploadingTAT.value = false
    return
  }

  try {
    const fd = new FormData()
    fd.append('file', tatFile.value)

    const res = await apiFetch(`${apiBase}/api/text-a-true/upload/${coursId.value}`, {
      method: 'POST',
      body: fd
    })

    successMessage.value = res?.message || 'Import réussi'
    showUploadTAT.value = false

    await fetchTAT()
    showTATViewer.value = true
  } catch (e) {
    uploadError.value = e.message || 'Erreur import CSV'
  } finally {
    isUploadingTAT.value = false
  }
}

const submitQCMUpload = async () => {
  if (!qcmFile.value) return
  isUploadingQCM.value = true
  uploadError.value = ''
  error.value = ''
  successMessage.value = ''

  if (!qcmFile.value.name.toLowerCase().endsWith('.csv')) {
    uploadError.value = 'Le fichier doit être .csv'
    isUploadingQCM.value = false
    return
  }

  try {
    const fd = new FormData()
    fd.append('file', qcmFile.value)

    const res = await apiFetch(`${apiBase}/api/qcm/upload/${coursId.value}`, {
      method: 'POST',
      body: fd
    })

    successMessage.value = res?.message || 'Import QCM réussi'
    showUploadQCM.value = false

    await fetchQCM()
    showQCMViewer.value = true
  } catch (e) {
    uploadError.value = e.message || 'Erreur import CSV QCM'
  } finally {
    isUploadingQCM.value = false
  }
}

const submitClassementUpload = async () => {
  if (!classementFile.value) return
  isUploadingClassement.value = true
  uploadError.value = ''
  error.value = ''
  successMessage.value = ''

  if (!classementFile.value.name.toLowerCase().endsWith('.csv')) {
    uploadError.value = 'Le fichier doit être .csv'
    isUploadingClassement.value = false
    return
  }

  try {
    const fd = new FormData()
    fd.append('file', classementFile.value)

    const res = await apiFetch(`${apiBase}/api/jeu-classement/upload/${coursId.value}`, {
      method: 'POST',
      body: fd
    })

    successMessage.value = res?.message || 'Import Jeu à Classement réussi'
    showUploadClassement.value = false

    await fetchClassement()
    showClassementViewer.value = true
  } catch (e) {
    uploadError.value = e.message || 'Erreur import CSV Jeu à Classement'
  } finally {
    isUploadingClassement.value = false
  }
}

const openTATViewer = async () => {
  showTATViewer.value = true
  if (tatQuestions.value.length === 0) await fetchTAT()
}

const openQCMViewer = async () => {
  showQCMViewer.value = true
  if (qcmQuestions.value.length === 0) await fetchQCM()
}

const openClassementViewer = async () => {
  showClassementViewer.value = true
  if (classementQuestions.value.length === 0) await fetchClassement()
}

const closeTATViewer = () => {
  showTATViewer.value = false
}

const closeQCMViewer = () => {
  showQCMViewer.value = false
}

const closeClassementViewer = () => {
  showClassementViewer.value = false
}

const toggleTAT = (id) => {
  openTATId.value = openTATId.value === id ? null : id
}

const toggleQCM = (id) => {
  openQCMId.value = openQCMId.value === id ? null : id
}

const toggleClassement = (id) => {
  openClassementId.value = openClassementId.value === id ? null : id
}

const deleteTAT = async (id) => {
  if (!confirm('Supprimer cette question ?')) return
  error.value = ''
  successMessage.value = ''
  try {
    await apiFetch(`${apiBase}/api/text-a-true/${id}`, { method: 'DELETE' })
    tatQuestions.value = tatQuestions.value.filter(q => q.id !== id)
    if (openTATId.value === id) openTATId.value = tatQuestions.value[0]?.id ?? null
    successMessage.value = 'Question supprimée'
  } catch (e) {
    error.value = e.message || 'Erreur suppression question'
  }
}

const deleteQCM = async (id) => {
  if (!confirm('Supprimer cette question QCM ?')) return
  error.value = ''
  successMessage.value = ''
  try {
    await apiFetch(`${apiBase}/api/qcm/${id}`, { method: 'DELETE' })
    qcmQuestions.value = qcmQuestions.value.filter(q => q.id !== id)
    if (openQCMId.value === id) openQCMId.value = qcmQuestions.value[0]?.id ?? null
    successMessage.value = 'Question QCM supprimée'
  } catch (e) {
    error.value = e.message || 'Erreur suppression question QCM'
  }
}

const deleteClassement = async (id) => {
  if (!confirm('Supprimer cette question de classement ?')) return
  error.value = ''
  successMessage.value = ''
  try {
    await apiFetch(`${apiBase}/api/jeu-classement/${id}`, { method: 'DELETE' })
    classementQuestions.value = classementQuestions.value.filter(q => q.id !== id)
    if (openClassementId.value === id) openClassementId.value = classementQuestions.value[0]?.id ?? null
    successMessage.value = 'Question de classement supprimée'
  } catch (e) {
    error.value = e.message || 'Erreur suppression question de classement'
  }
}

// ---------- Navigation ----------
const refreshAll = async () => {
  await Promise.all([fetchCours(), fetchPages(), fetchTAT(), fetchQCM(), fetchClassement()])
}
const goBack = () => router.go(-1)

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  router.push('/login')
}

// ---------- Init ----------
onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }
  await Promise.all([fetchCours(), fetchPages(), fetchTAT(), fetchQCM(), fetchClassement()])
})
</script>

<style scoped>
/* Header */
.header-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: .08em;
  font-size: 12px;
  color: #667eea;
  margin: 0 0 6px;
  font-weight: 800;
}

.subtitle {
  margin: 6px 0 0;
  color: #555;
}

/* Alerts */
.error-bar,
.success-bar {
  padding: 12px 16px;
  border-radius: 10px;
  margin-bottom: 12px;
  border: 1px solid;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.error-bar {
  background: #ffe3e3;
  color: #b00020;
  border-color: #ffb3b3;
}

.success-bar {
  background: #e7fff1;
  color: #0a6b2b;
  border-color: #b6f2cb;
}

.close-x {
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 20px;
  line-height: 1;
  color: inherit;
}

/* Panels */
.panel {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, .08);
  margin-bottom: 20px;
  overflow: hidden;
}

.panel-head {
  background: #fafafa;
  border-bottom: 1px solid #eee;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
}

.panel-title h3 {
  margin: 0;
  color: #222;
}

.icon {
  font-size: 20px;
}

.panel-body {
  padding: 16px;
}

/* Cards */
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  margin-top: 10px;
}

.card {
  background: white;
  padding: 18px;
  border-radius: 14px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, .08);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-icon {
  font-size: 2rem;
}

.description {
  color: #555;
  margin: 0;
  white-space: pre-wrap;
}

.meta {
  color: #777;
  font-size: .9rem;
  margin: 0;
}

.card-actions {
  margin-top: auto;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.edit-box {
  background: #f8f9ff;
  border: 1px solid #d8ddff;
  padding: 12px;
  border-radius: 12px;
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.edit-box label {
  font-weight: 800;
  color: #333;
  font-size: 0.9rem;
}

/* Buttons */
.danger {
  background: #ffeded;
  color: #b00020;
  border: 1px solid #ffb3b3;
  border-radius: 10px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 800;
}

.danger:disabled {
  opacity: .7;
  cursor: not-allowed;
}

/* Inputs */
.input,
.textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  font-size: 1rem;
  background: #fafafa;
}

.textarea {
  resize: vertical;
}

.field {
  display: grid;
  gap: 6px;
  margin-top: 12px;
}

.field span {
  font-size: .9rem;
  color: #444;
  font-weight: 700;
}

/* Loading + empty */
.loading {
  display: flex;
  align-items: center;
  gap: 10px;
  color: #555;
}

.empty {
  display: grid;
  gap: 8px;
  color: #666;
}

/* Spinner */
.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, .15);
  border-top-color: rgba(0, 0, 0, .5);
  border-radius: 50%;
  animation: spin .8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Badge / pill */
.badge {
  background: #eef0ff;
  color: #667eea;
  font-size: 12px;
  font-weight: 900;
  padding: 2px 8px;
  border-radius: 999px;
}

.pill {
  background: #f3f4ff;
  color: #4a55e6;
  font-size: 12px;
  font-weight: 900;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid #d8ddff;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, .4);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 50;
}

.modal {
  width: 100%;
  max-width: 640px;
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, .15);
  padding: 20px;
}

.modal-big {
  max-width: 900px;
}

.modal-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.modal-top-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* Game picker */
.game-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.game-tile {
  border: 1px solid #eee;
  background: #fafafa;
  border-radius: 14px;
  padding: 14px;
  cursor: pointer;
  text-align: left;
  transition: transform .15s, border-color .15s, box-shadow .15s;
}

.game-tile:hover {
  transform: translateY(-1px);
  border-color: #d8ddff;
  box-shadow: 0 8px 18px rgba(0, 0, 0, .06);
}

.game-emoji {
  font-size: 26px;
}

.game-title {
  font-weight: 900;
  color: #222;
  margin-top: 6px;
}

.game-desc {
  color: #666;
  font-size: 13px;
  margin-top: 2px;
}

/* Game cards */
.game-card {
  cursor: pointer;
  transition: transform .15s, box-shadow .15s;
}

.game-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, .08);
}

.game-card.disabled {
  opacity: .6;
  cursor: not-allowed;
}

.game-card.disabled:hover {
  transform: none;
  box-shadow: 0 4px 15px rgba(0, 0, 0, .08);
}

/* Accordion */
.tat-accordion {
  display: grid;
  gap: 10px;
}

.qcm-accordion {
  display: grid;
  gap: 10px;
}

.classement-accordion {
  display: grid;
  gap: 10px;
}

.acc-item {
  border: 1px solid #eee;
  border-radius: 14px;
  overflow: hidden;
  background: #fff;
}

.acc-item.open {
  border-color: #d8ddff;
  box-shadow: 0 8px 20px rgba(0, 0, 0, .06);
}

.acc-head {
  width: 100%;
  border: none;
  background: #fafafa;
  padding: 12px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.acc-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.acc-index {
  font-weight: 900;
  color: #667eea;
  background: #eef0ff;
  border-radius: 999px;
  padding: 4px 8px;
  font-size: 12px;
}

.acc-text {
  color: #222;
  font-weight: 800;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.acc-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.chev {
  font-size: 18px;
  color: #667eea;
  font-weight: 900;
}

.acc-body {
  padding: 14px;
}

/* Elements styling for classement */
.elements {
  display: grid;
  gap: 8px;
  margin-bottom: 12px;
}

.element {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 8px;
}

.element-number {
  font-weight: 700;
  color: #667eea;
  min-width: 20px;
}

.answers {
  display: grid;
  gap: 8px;
}

.answer {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: #fafafa;
  border: 1px solid #eee;
}

.answer.correct {
  background: #f2fff7;
  border-color: #b6f2cb;
}

.answer-letter {
  font-weight: 900;
  color: #667eea;
  width: 28px;
}

.explain {
  margin-top: 10px;
  background: #fafafa;
  border-left: 4px solid #667eea;
  padding: 10px 12px;
  border-radius: 12px;
  color: #444;
}

.acc-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.modal-footer-lite {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.skeleton {
  position: relative;
  overflow: hidden;
}

.skeleton::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, .6), transparent);
  animation: shimmer 1.5s infinite;
}

.skeleton-line {
  height: 14px;
  background: #ececec;
  border-radius: 6px;
  margin: 8px 0;
}

.skeleton-line.title {
  width: 70%;
  height: 18px;
}

.skeleton-line.short {
  width: 40%;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }

  100% {
    transform: translateX(100%);
  }
}

@media (max-width:768px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }

  .game-grid {
    grid-template-columns: 1fr;
  }

}
</style>
